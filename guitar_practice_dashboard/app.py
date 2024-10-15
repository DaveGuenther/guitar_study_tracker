# Core
from pathlib import Path
import pandas as pd
import numpy as np
import os
import datetime
import pytz
from dotenv import load_dotenv


# Web/Visual frameworks
from shiny import App, ui, render, reactive, types, req, module
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from shinywidgets import output_widget, render_widget, render_plotly

# App Specific Code
import orm # database models
from database import DatabaseSession, DatabaseModel
import data_prep
import filter_shelf



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
session_model.df_raw= pd.read_csv('data.csv') # remove when done testing
df_sessions = data_prep.processData(session_model, song_model, artist_model, style_model)



app_ui = ui.page_fluid(
        ui.tags.link(href='styles.css', rel="stylesheet"),

        ui.div(
            ui.page_navbar(
                # Execute ui code for shiny modules
                ui.nav_panel("Practice Sessions", 
                    ui.h3("Total Practice Time (Minutes) per Day"),
                    ui.div(
                        output_widget(id='waffle_chart'),
                        ui.img(src='guitar-stock-transparent-min.png', width="600px"),
                        id='guitar-neck-container',
                    ).add_style('width:1850px; overflow-x: auto; display: flex; margin:0px; padding:0px;'),
                ), 
                ui.nav_panel("Career Repertoire",
                    "Career Repretoire",
                    ui.sidebar(
                        ui.h4("Filters"),
                        filter_shelf.filter_shelf(df_sessions),
                        width=300,
                    ),
                ), 
            id='main_nav_bar',     
            title="Guitar Study Tracker Dashboard",
            ),
        ),
        title="Guitar Study Tracker Dashboard"

        
        


)

def server(input, output, session):
    
    df_session_data = reactive.value(df_sessions)

    @reactive.calc
    def df_sessions_stage_1():
        '''
        This returns the df_sessions dataframe with only filter shelf filters applied (Stage 1).
        '''
        df_filtered = df_sessions
        return df_filtered

    @reactive.calc
    def heatMapDataTranform():
        pd.set_option('future.no_silent_downcasting', True) # needed for fillna() commands below
        today = datetime.datetime.now(pytz.timezone('US/Eastern')).date()
        #prep for heatmap
        df_grouped = df_sessions_stage_1()[['Weekday_abbr','session_date','month_abbr', 'has_url','week_start_day_num','month_week_start','Year','month_year', 'Duration']].groupby(['Weekday_abbr','Year','month_abbr','month_year','session_date','has_url','week_start_day_num','month_week_start'], as_index=False).sum()
        df_grouped = df_grouped[df_grouped['session_date']>=today-pd.DateOffset(days=365)]
        df_grouped = df_grouped.sort_values(['session_date'])
        #df_pivoted = df_grouped.pivot(index=['Weekday_abbr'], columns=['month_year','week_start_day_num']) # produces a nested axis grid with a "df" for every column passed in (Duration, session_date, Year, etc).
        df_pivoted = df_grouped.pivot(index=['Weekday_abbr'], columns=['Year','month_year','month_week_start']) # produces a nested axis grid with a "df" for every column passed in (Duration, session_date, Year, etc).

        #create weekdays by week number grid to build a githubt style activity waffle chart
        df_durations = df_pivoted.T[df_pivoted.T.index.get_level_values(0)=='Duration'].T  # isolate the Duration grid
        df_durations = df_durations.loc[['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],]
        df_durations = df_durations.fillna('')

        #create weekdays by week number grid to build a githubt style activity waffle chart
        df_session_dates = df_pivoted.T[df_pivoted.T.index.get_level_values(0)=='session_date'].T  # isolate the session_date grid
        df_session_dates = df_session_dates.loc[['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],]
        df_session_dates = df_session_dates.fillna('')

        #create weekdays by week number grid to build a githubt style activity waffle chart
        df_has_urls = df_pivoted.T[df_pivoted.T.index.get_level_values(0)=='has_url'].T  # isolate the session_date grid
        df_has_urls = df_has_urls.loc[['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],]
        df_has_urls = df_has_urls.fillna('')


        def getDateString(cell):
            if cell:
                return cell.strftime('%a %m-%d-%Y')
            return ''

        #create weekdays by week number grid to build a githubt style activity waffle chart
        df_str_session_dates = df_pivoted.T[df_pivoted.T.index.get_level_values(0)=='session_date'].T  # isolate the session_date grid
        df_str_session_dates = df_session_dates.loc[['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],]
        df_str_session_dates = df_session_dates.fillna('')
        df_str_session_dates = df_str_session_dates.map(getDateString) # nice formatted string for the Hover of the heatmap

        years = list(df_durations.T.index.get_level_values(1))
        month_week_starts = list(df_durations.T.index.get_level_values(3))
        #month_year_names = list(df_durations.T.index.get_level_values(1)) # this list contains the Month/Year (e.g. "Oct '24") of the sunday of each week (each week is a column) in the grid in ascending order
        week_start_day_nums = list(df_durations.T.index.get_level_values(2)) # this list contains the day of the month that starts the week (each week is a column) in the grid in ascending order

        ret_dict = {
            'Week Names':[years,month_week_starts],#,week_start_day_nums], # establishes a 2-level axis grouping the like month/years together
            'Weekday Names':list(df_durations.index),
            'Daily Practice Durations Grid':[list(df_durations.loc[wk_day,]) for wk_day in df_durations.index],
            'customdata':[
                [list(df_session_dates.loc[wk_day,]) for wk_day in df_session_dates.index], # datetimes
                [list(df_str_session_dates.loc[wk_day,]) for wk_day in df_str_session_dates.index], # Dates as formatted strings
                [list(df_has_urls.loc[wk_day,]) for wk_day in df_has_urls.index], # '*' for days with a video URL
            ],
        }
        
        return ret_dict


    @render_widget
    def waffle_chart():
        ret_dict = heatMapDataTranform()
        num_columns = len(ret_dict['Week Names'][0])
        print(num_columns)
        # add subplot here for year as stacked bar

        fig = go.Figure(
            go.Heatmap(
                x=ret_dict['Week Names'],
                y=ret_dict['Weekday Names'],
                z=ret_dict['Daily Practice Durations Grid'],     
                customdata=np.stack((ret_dict['customdata'][0], ret_dict['customdata'][1], ret_dict['customdata'][2]), axis=-1),
                text=ret_dict['customdata'][2],
                texttemplate="%{text}",
                textfont={'size':14},
                hovertemplate='Date: %{customdata[1]}<br>Duration (Minutes): %{z}',           
                xgap=5,
                ygap=5,
                hoverongaps=False,
                zmin=0,
                zmax=60,
                colorscale=[[0.0, "#40291D"], [1.0, "#03A9F4"]],
                colorbar= dict(
                    title="Minutes",
                    tickmode= 'array',
                    tickvals= [0,30,60],
                    ticktext=["0","30","60"],
                    thickness=12,
                    x=-0.085,
                ),
                
            ),
        )

        fig.update_layout(
            margin=dict(t=100, b=0, l=0, r=0),
            xaxis_side='bottom',
            xaxis_dtick=1, 
            
            # Main plot styling
            font_family='garamond',
            font_color='#B2913C',
            paper_bgcolor='#000000',
            
           
            yaxis_dtick=1,
            autosize=False,
            width=1150,#75+(30*num_columns),#1635 if 75+(30*num_columns)>1635 else 75+(30*num_columns),
            height=320,
            plot_bgcolor="#40291D",

    
        )
        fig.layout.xaxis.fixedrange = True
        fig.layout.yaxis.fixedrange = True

        fig.update_xaxes(
            #title="Week of",
            gridcolor="#6f340d",
            tickangle=285,
            anchor='free',
            position=0,


        )
        fig.update_yaxes(
            gridcolor="rgba(.5,.5,.5,.1)",

        )
        figWidget = go.FigureWidget(fig)
        return figWidget

app_dir = Path(__file__).parent
app = App(app_ui, server, debug=False, static_assets=app_dir / "www")
