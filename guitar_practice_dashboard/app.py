# Core
from pathlib import Path
import math
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
#session_model.df_raw= pd.read_csv('data.csv') # remove when done testing
df_sessions, df_365 = data_prep.processData(session_model, song_model, artist_model, style_model)



app_ui = ui.page_fluid(
        ui.tags.link(href='styles.css', rel="stylesheet"),
        ui.div(
            ui.page_navbar(
                # Execute ui code for shiny modules
                ui.nav_panel("Practice Sessions", 
                    ui.card(
                        ui.div(
                            output_widget(id='waffle_chart'),
                            ui.img(src='guitar-head-stock.png', width="485px", height="252"),
                            id='guitar-neck-container',
                        ).add_style('width:1800px; overflow-x: auto; display: flex; margin:0px; padding:0px;'),
                        class_="dashboard-card",
                    ),

                    ui.row(
                        ui.column(6,
                            ui.card(
                                ui.h3("Time Spent Practicing Songs (Past Year)"),
                                output_widget(id='last_year_bar_chart'),
                                class_="dashboard-card",
                            ),
                            ui.h6("Dave Guenther, 2024"),
                        ),
                        ui.column(6,
                            ui.card(
                                ui.h3("Practice Session Notes (Past Week)").add_style("color:#Ff9b15;"),
                                output_widget(id='last_week_bar_chart').add_style('height:200px; overflow-y: auto; display: flex;'),
                                ui.output_data_frame(id="sessionNotesTable").add_class('dashboard-table'),
                                class_="dashboard-card",
                            ),
                            
                        ),
                    )
                ), 
                ui.nav_panel("Career Repertoire",
                    "Career Repretoire",
                    ui.sidebar(
                        ui.h4("Filters"),
                        filter_shelf.filter_shelf(df_sessions),
                        width=300,
                    ),
                    ui.row(
                        ui.column(3,
                            ui.card(
                                ui.h4("Avg. Practice Time/Day"),

                            ),
                        ),
                        ui.column(2,
                            ui.card(
                                ui.h4("Longest Practice Streak"),

                            ),                        

                        ),
                        ui.column(2,
                            ui.card(
                                ui.h4("Longest Session"),

                            ),
                        ),
                        ui.column(3,
                            ui.card(
                                ui.h4("Total Career Practice Time"),

                            ),
                        ),
                        ui.column(2,
                            ui.card(
                                ui.h4("Year:"),

                            ),
                        ),                                                                                                
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
    def df_365_stage_1():
        '''
        This returns the df_sessions dataframe with only filter shelf filters applied (Stage 1).
        '''
        df_filtered = df_365
        return df_filtered

    @reactive.calc
    def sessionNotesTransform():
        today = datetime.datetime.now(pytz.timezone('US/Eastern')).date()
        df_session_notes = df_sessions[df_sessions['session_date']>=today-pd.DateOffset(days=7)]
        df_session_notes = df_session_notes.sort_values('session_date')
        df_song_sort_lookup = df_session_notes.groupby(['Song'], as_index=False)[['Duration']].sum().sort_values('Duration', ascending=False).reset_index(drop=True).reset_index()[['Song','index']]
        df_session_notes = pd.merge(df_session_notes, df_song_sort_lookup, how='left', on="Song")
        df_session_notes = df_session_notes.sort_values(['index','session_date'])
        df_out = df_session_notes[['Song','Session Date','Notes','Duration']]
        return df_out.copy()

    @render.data_frame
    def sessionNotesTable():
        df_out = sessionNotesTransform()
        return render.DataTable(df_out, width="100%", height="250px", styles=[{'class':'dashboard-table'}])

    @reactive.calc
    def heatMapDataTranform():
        pd.set_option('future.no_silent_downcasting', True) # needed for fillna() commands below
        today = datetime.datetime.now(pytz.timezone('US/Eastern')).date()
        #prep for heatmap
        
        df_grouped = df_365_stage_1()[['Weekday_abbr','session_date','month_abbr', 'has_url','week_start_day_num','month_week_start','Year','month_year', 'Duration']].groupby(['Weekday_abbr','Year','month_abbr','month_year','session_date','has_url','week_start_day_num','month_week_start'], as_index=False).sum()
        
        df_grouped = df_grouped.sort_values(['session_date'])
        df_pivoted = df_grouped.pivot(index=['Weekday_abbr'], columns=['Year','month_year','month_week_start']) # produces a nested axis grid with a "df" for every column passed in (Duration, session_date, Year, etc).

        #Establish Durations (minutes/day) for github style activity waffle chart
        df_durations = df_pivoted.T[df_pivoted.T.index.get_level_values(0)=='Duration'].T  # isolate the Duration grid
        df_durations = df_durations.loc[['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],]
        df_durations = df_durations.fillna('')

        #Establish session dates for github style activity waffle chart
        df_session_dates = df_pivoted.T[df_pivoted.T.index.get_level_values(0)=='session_date'].T  # isolate the session_date grid
        df_session_dates = df_session_dates.loc[['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],]
        df_session_dates = df_session_dates.fillna('')

        #establish has_url column that we'll use to print Asterisks for githube style waffle chart
        df_has_urls = df_pivoted.T[df_pivoted.T.index.get_level_values(0)=='has_url'].T  # isolate the session_date grid
        df_has_urls = df_has_urls.loc[['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],]
        df_has_urls = df_has_urls.fillna('')


        def getDateString(cell):
            if cell:
                return cell.strftime('%a %m-%d-%Y')
            return ''

        #Establish Strings of dates for tooltips for github style activity waffle chart
        df_str_session_dates = df_pivoted.T[df_pivoted.T.index.get_level_values(0)=='session_date'].T  # isolate the session_date grid
        df_str_session_dates = df_session_dates.loc[['Mon','Tue','Wed','Thu','Fri','Sat','Sun'],]
        df_str_session_dates = df_session_dates.fillna('')
        df_str_session_dates = df_str_session_dates.map(getDateString) # nice formatted string for the Hover of the heatmap

        years = list(df_durations.T.index.get_level_values(1))
        month_week_starts = list(df_durations.T.index.get_level_values(3))
        
        ret_dict = {
            'Week Names':[years,month_week_starts], # establishes a 2-level axis grouping the like years together
            'Weekday Names':list(df_durations.index),
            'Daily Practice Durations Grid':[list(df_durations.loc[wk_day,]) for wk_day in df_durations.index],
            'customdata':[
                [list(df_session_dates.loc[wk_day,]) for wk_day in df_session_dates.index], # datetimes
                [list(df_str_session_dates.loc[wk_day,]) for wk_day in df_str_session_dates.index], # Dates as formatted strings
                [list(df_has_urls.loc[wk_day,]) for wk_day in df_has_urls.index], # '*' for days with a video URL
            ],
        }
        
        return ret_dict

    @reactive.calc
    def lastYearSongTransform():
        df_365 = df_365_stage_1()
        df_365 = df_365[df_365['Song'].notna()]
        df_365 = df_365.groupby(['Song','Composer','Arranger'], as_index=False)['Duration'].sum()
        df_365['Minutes'] = df_365['Duration']%60
        df_365['Hours'] = (df_365['Duration']/60).apply(math.floor)
        df_365['Duration']=df_365['Duration']/60
        return df_365

    @render_widget
    def last_year_bar_chart():
        df_365_songs = lastYearSongTransform()
        custom_data = [
            [composer, arranger, hours, minutes] for composer, arranger, hours, minutes in zip(
                list(df_365_songs['Composer']),
                list(df_365_songs['Arranger']),
                list(df_365_songs['Hours']),
                list(df_365_songs['Minutes']))
        ]

        
        fig = go.Figure(go.Bar(
            x=df_365_songs['Duration'], 
            y=df_365_songs['Song'], 
            orientation='h',
            marker=dict(cornerradius=30),         
            customdata=custom_data
        ))
        fig.update_traces(
            marker_color="#03A9F4",
            hovertemplate="""
                <b>Song:</b> %{y}<br>
                Composer: %{customdata[0]}<br>
                Arranger: %{customdata[1]}<br>
                Total Practice Time: %{customdata[2]} Hours, %{customdata[3]} Minutes
                <extra></extra>
            """,
        )  
        fig.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            dragmode=False,
            modebar=dict(remove=['zoom2d','pad2d','select2d','lasso2d','zoomIn2d','zoomOut2d','autoScale2d']),
            
            # Main plot styling
            font_family='garamond',
            font_color='#Ff9b15',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            
            height=500,
            plot_bgcolor="rgba(0, 0, 0, 0)",
        )              
        fig.update_xaxes(title_text='Practice Time (Hours)')
        fig.layout.xaxis.fixedrange = True
        fig.layout.yaxis.fixedrange = True

        figWidget = go.FigureWidget(fig)
        return figWidget



    @render_widget
    def last_week_bar_chart():
        df_last_week = sessionNotesTransform()
        df_bar_summary = df_last_week.groupby('Song',as_index=False)[['Duration']].sum()
        df_bar_summary = df_bar_summary.sort_values("Duration", ascending=True)
        fig = go.Figure(go.Bar(
            x=df_bar_summary['Duration'], 
            y=df_bar_summary['Song'], 
            orientation='h',
            marker=dict(cornerradius=30),         
            
            ))
        fig.update_traces(
            marker_color="#03A9F4",
            hovertemplate='Song: %{y}<br>Practice Time (Minutes): %{x}<extra></extra>',
        )
        fig.update_layout(
            margin=dict(t=0, b=0, l=0, r=0),
            dragmode=False,
            modebar=dict(remove=['zoom2d','pad2d','select2d','lasso2d','zoomIn2d','zoomOut2d','autoScale2d']),
            
            # Main plot styling
            font_family='garamond',
            font_color='#Ff9b15',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            
            height=200,
            plot_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_xaxes(title_text='Practice Time (Minutes)')
        fig.layout.xaxis.fixedrange = True
        fig.layout.yaxis.fixedrange = True

        figWidget = go.FigureWidget(fig)
        return figWidget

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
            margin=dict(t=44, b=0, l=0, r=0),
            
            title=dict(text="Daily Practice Time (Past Year)",font=dict(size=30, color="#FFF8DC"),yanchor='bottom', yref='paper'),
            xaxis_side='bottom',
            xaxis_dtick=1, 
            
            # Main plot styling
            font_family='garamond',
            font_color='#Ff9b15',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            
           
            yaxis_dtick=1,
            autosize=False,
            width=1250,#75+(30*num_columns),#1635 if 75+(30*num_columns)>1635 else 75+(30*num_columns),
            height=277,
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
