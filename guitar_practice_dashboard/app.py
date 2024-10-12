# Core
import pandas as pd
import numpy as np
import os
from dotenv import load_dotenv
import logging

# Web/Visual frameworks
from shiny import App, ui, render, reactive, types, req, module
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from shinywidgets import output_widget, render_widget, render_plotly

# App Specific Code
import orm # database models
from database import DatabaseSession, DatabaseModel
import data_prep

#logging.basicConfig(filename='myapp.log', level=logging.INFO)

# pull database location and credential information from env variables
load_dotenv("variables.env")

# Establish database session minus credentials
pg_session = DatabaseSession(
    os.getenv("pg_host"),
    os.getenv("pg_port"),
    os.getenv("pg_dbname")
    )

# Create object relational mappings for the three database tables
artist_model = DatabaseModel(orm.tbl_artist, pg_session)
style_model = DatabaseModel(orm.tbl_style, pg_session)
song_model = DatabaseModel(orm.tbl_song, pg_session)
session_model = DatabaseModel(orm.tbl_practice_session, pg_session)

user_name = os.getenv('pg_user')
pw = os.getenv('pg_pw')

artist_model.connect(user_name, pw, True)
style_model.connect(user_name, pw, True)
song_model.connect(user_name, pw, True)
session_model.connect(user_name, pw, True)

df_sessions = data_prep.processData(session_model, song_model, artist_model, style_model)



app_ui = ui.page_fluid(
    ui.page_sidebar(
        ui.sidebar(
            ui.h4("Filters")
        ),
        ui.div(
            ui.page_navbar(
                # Execute ui code for shiny modules
                ui.nav_panel("Practice Sessions", 
                    "Practice Sessions",
                    ui.div(
                        output_widget(id='waffle_chart').add_style('horizontal-align:right;'),
                    ),
                ), 
                ui.nav_panel("Career Repertoire",
                    "Career Repretoire",
                ),      
            ),
        ),
        title="Guitar Study Tracker Dashboard"
    ),
        
        


)

def server(input, output, session):
    
    df_session_data = reactive.value(df_sessions)

    @reactive.calc
    def filter_stage_1():
        pass

    @reactive.calc
    def heatMapDataTranform():
        pd.set_option('future.no_silent_downcasting', True) # needed for fillna() commands below
        
        #prep for heatmap
        df_grouped = df_sessions[['Weekday_abbr','session_date','week_start_day_num','Year','month_year', 'Duration']].groupby(['Weekday_abbr','Year','month_year','session_date','week_start_day_num'], as_index=False).sum()
        df_grouped = df_grouped.sort_values(['Year','session_date'])#.drop('session_date',axis=1)
        df_pivoted = df_grouped.pivot(index=['Weekday_abbr'], columns=['month_year','week_start_day_num']) # produces a nested axis grid with a "df" for every column passed in (Duration, session_date, Year, etc).
        
        #create weekdays by week number grid to build a githubt style activity waffle chart
        df_durations = df_pivoted.T[df_pivoted.T.index.get_level_values(0)=='Duration'].T  # isolate the Duration grid
        df_durations = df_durations.loc[['Sun','Mon','Tue','Wed','Thu','Fri','Sat'],]
        df_durations = df_durations.fillna('')

        #create weekdays by week number grid to build a githubt style activity waffle chart
        df_session_dates = df_pivoted.T[df_pivoted.T.index.get_level_values(0)=='session_date'].T  # isolate the session_date grid
        df_session_dates = df_session_dates.loc[['Sun','Mon','Tue','Wed','Thu','Fri','Sat'],]
        df_session_dates = df_session_dates.fillna('')

        def getDateString(cell):
            if cell:
                return cell.strftime('%a %m-%d-%Y')
            return ''

        #create weekdays by week number grid to build a githubt style activity waffle chart
        df_str_session_dates = df_pivoted.T[df_pivoted.T.index.get_level_values(0)=='session_date'].T  # isolate the session_date grid
        df_str_session_dates = df_session_dates.loc[['Sun','Mon','Tue','Wed','Thu','Fri','Sat'],]
        df_str_session_dates = df_session_dates.fillna('')
        df_str_session_dates = df_str_session_dates.map(getDateString) # nice formatted string for the Hover of the heatmap

        month_year_names = list(df_durations.T.index.get_level_values(1)) # this list contains the Month/Year (e.g. "Oct '24") of the sunday of each week (each week is a column) in the grid in ascending order
        week_start_day_nums = list(df_durations.T.index.get_level_values(2)) # this list contains the day of the month that starts the week (each week is a column) in the grid in ascending order

        ret_dict = {
            'Week Names':[month_year_names,week_start_day_nums], # establishes a 2-level axis grouping the like month/years together
            'Weekday Names':list(df_durations.index),
            'Daily Practice Durations Grid':[list(df_durations.loc[wk_day,]) for wk_day in df_durations.index],
            'customdata':[
                [list(df_session_dates.loc[wk_day,]) for wk_day in df_session_dates.index], # datetimes
                [list(df_str_session_dates.loc[wk_day,]) for wk_day in df_str_session_dates.index], # Dates as formatted strings
            ],
        }
        
        return ret_dict


    @render_widget
    def waffle_chart():
        ret_dict = heatMapDataTranform()
        num_columns = len(ret_dict['Week Names'])
        
        # add subplot here for year as stacked bar

        fig = go.Figure(
            go.Heatmap(
                x=ret_dict['Week Names'],
                y=ret_dict['Weekday Names'],
                z=ret_dict['Daily Practice Durations Grid'],     
                customdata=np.stack((ret_dict['customdata'][0], ret_dict['customdata'][1]), axis=-1),
                hovertemplate='Date: %{customdata[1]}<br>Duration (Minutes): %{z}',           
                xgap=5,
                ygap=5,
                hoverongaps=False,
                zmin=20,
                zmax=70,
                colorscale=[[0.00, "red"],   [0.2, "red"],
                            [0.2, "orange"], [0.8, "blue"],
                            [0.8, "darkblue"],  [1.00, "darkblue"]],
                colorbar= dict(
                    tick0= 0,
                    tickmode= 'array',
                    tickvals= [25,30,40,50,60,65],
                    ticktext=["<30","30","40","50","60",">60"],
                    tickwidth=40,
                    xpad=10,
                    thickness=25,
                    
                )
            )   
        )

        fig.update_layout(
            margin=dict(t=100, b=0, l=00, r=0),
            xaxis_side='bottom',
            xaxis_dtick=1,

            
           
            yaxis_dtick=1,
            autosize=False,
            width=150+(50*num_columns),
            height=300,
            plot_bgcolor="rgba(.5,.5,.5,.2)",
            
            
        )
        fig.update_xaxes(
            gridcolor="rgba(.5,.5,.5,.1)",
            #tickangle=315,
            anchor='free',
            position=0,

        )
        fig.update_yaxes(
            gridcolor="rgba(.5,.5,.5,.1)",

        )
        figWidget = go.FigureWidget(fig)
        return figWidget




app = App(app_ui, server, debug=True)
