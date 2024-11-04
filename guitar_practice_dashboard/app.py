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
from shiny.types import ImgData
from faicons import icon_svg

# App Specific Code

import orm # database models
from database import DatabaseSession, DatabaseModel
import data_prep
import ui_extension

import logger
Logger = logger.FunctionLogger
Logger.setLogger(False) # turn off the shinylogger

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
        ui.HTML('<meta property="og:image" content="rosette-whole-small-min.png" />'),
        ui.tags.link(href='styles.css', rel="stylesheet"),
        ui.tags.link(href='flex.css', rel="stylesheet"),
        ui.div(
            ui.page_navbar(
                ui_extension.tab_session(df_365),
                # Execute ui code for shiny modules
                ui_extension.tab_career(df_sessions),
                ui.nav_panel(
                    "Acoustic Arsenal",
                    "Acoustic Arsenal",
                    "-=Guitar=-",
                    "-=Current Strings=-",
                    "-=Strings Installed on=-",
                    "-=Play Time on Strings=-",

                ),
                ui.nav_panel(
                    "About",
                    "About"

                ),                
            id='main_nav_bar',     
            title="Guitar Study Tracker",
            ),
        ),
        title="Guitar Study Tracker"

)

def table_calc_has_url(df_in):
    df_grouped_by_date = df_in.groupby('session_date') # grouped by date in order to capture an '*' if ANY recording weas posted that day
    ser_has_url = df_grouped_by_date['Video URL'].transform(lambda group: '*' if any(group.values) else'')
    return pd.Series(ser_has_url, name='has_url')

def server(input, output, session):
    Logger(session.ns)
    df_session_data = reactive.value(df_sessions)

    @reactive.calc
    def df_365_stage_1():
        '''
        This returns the df_sessions dataframe with only filter shelf filters applied (Stage 1).
        '''
        Logger(session.ns)
        df_filtered = df_365
        df_filtered = df_365[(df_365['Song'].isin(input.song_title()))|(df_365['Song'].isna())]
        return df_filtered

    @module.ui
    def create_video_button():
        Logger(session.ns)
        return ui.div(ui.output_image(id=f'video_image', height='50px', click=True))


    @module.server
    def video_icon_server(input, output, session, url:str, title:str):
        Logger(session.ns)
        print("entering video_icon_server()")
        #this_url = reactive.value(url)

        
        @render.image
        def video_image():
            Logger(session.ns)
            dir = Path(__file__).resolve().parent
            img: ImgData = {"src":str(dir / "www/video_camera.svg"),"height":"30px"}
            return img
        
        @reactive.effect
        @reactive.event(input.video_image_click)
        def showModal():
            Logger(session.ns)
            #with reactive.isolate():

            embed_url = url
            embed_url = embed_url[0:embed_url.find('?')]
            embed_url = embed_url.replace('https://youtu.be/','https://youtube.com/embed/')
            
            m = ui.modal(
                ui.div(
                    ui.h3(title).add_class("modal-title-text"),
                    ui.modal_button(label=None, icon=icon_svg("x")).add_class("modal-close", prepend=True), #you don't need to add the 'fa-' in front of the icon name
                ).add_class("modal-titlebar"),
                ui.HTML(f"""<iframe width="434" height="245" src="{embed_url}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>"""),
                easy_close=False,
                footer=None,
            )
            ui.modal_show(m)




   

    def sessionNotesTransform(from_date=(datetime.datetime.now(pytz.timezone('US/Eastern')).date()), 
                              num_days=7):
        """
        returns the session data table based on input parameters:
        from_date (datetime.datetime): This is the date to start providing session data from
        num_days (int): number of days before from_date to incldue data in the session table.
        namespace_slug (str): gets appended onto any modules that are created to track what widget they support.
        """
        #today = datetime.datetime.now(pytz.timezone('US/Eastern')).date()
        Logger(session.ns)
        df_session_notes = df_sessions[(df_sessions['session_date']>=from_date-pd.DateOffset(days=num_days))&(df_sessions['session_date']<=pd.Timestamp(from_date))]
        df_session_notes = df_session_notes.sort_values('session_date')
        df_song_sort_lookup = df_session_notes.groupby(['Song'], as_index=False)[['Duration']].sum().sort_values('Duration', ascending=False).reset_index(drop=True).reset_index()[['Song','index']]
        df_session_notes = pd.merge(df_session_notes, df_song_sort_lookup, how='left', on="Song")
        df_session_notes = df_session_notes.sort_values(['index','session_date'])
        
        df_out = df_session_notes[['id','Song','Session Date','Notes','Duration', 'Video URL']].reset_index()
        return df_out.copy()

    def add_URL_icon_to_session_table(df_in, namespace_slug=''):
        """
        This function establishes a reactive context!  Do not call from a non-reactive context unless you entend to make it reactive.
        This function establishes shiny modules for each row that has a Video URL.  The input is a dataframe with a URL column, and the output will be a dataframe with a Video Link column that has HTML formatted ui and runs a server function in the background.
        namespace_slug (str): gets appended onto any modules that are created to track what widget they support.
        """
        Logger(session.ns)

        def vid_link_module(row):
            #print("entering vid_link_module()")
            Logger(session.ns)
            namespace_id = namespace_slug+str(int(row['id']))
            if row['Video URL']:
                print('Creating module with slug', str(int(row['id'])))
                ret_html = create_video_button(namespace_id)
                video_title=str(row['Session Date']+" - "+row['Song'])
                video_icon_server(namespace_id,row['Video URL'], video_title)
                print('Created module with slug', namespace_id)
            else:
                ret_html = row['Video URL']
            #print("exiting vid_link_module()")
            return ret_html # return the HTML content for the video link cell
            
        df_out = df_in
        df_out['Video Link'] = df_out.apply(lambda row: vid_link_module(row), axis=1)
        return df_out.copy()

    @render.data_frame
    def sessionNotesTable():
        Logger(session.ns)
        df_out = sessionNotesTransform(num_days=7)
        df_out = add_URL_icon_to_session_table(df_out,"sessionNotesTable")
        df_out = df_out [['Song','Session Date','Notes','Duration',"Video Link"]]
        return render.DataTable(df_out, width="100%", styles=[{'class':'dashboard-table'}])



    @reactive.calc
    def heatMapDataTranform():
        Logger(session.ns)
        pd.set_option('future.no_silent_downcasting', True) # needed for fillna() commands below
        today = datetime.datetime.now(pytz.timezone('US/Eastern')).date()
        #prep for heatmap
        df_365_filtered = df_365_stage_1()

        # This is a table calculation to establish the 'has_url' columns that contains a * if any of the sessions on that date included a youtube recording
        has_url = table_calc_has_url(df_365_filtered.copy())
        df_365_filtered = pd.concat([df_365_filtered, has_url],axis=1) # adds the has_url column
        
        df_grouped = df_365_filtered[['Weekday_abbr','session_date','month_abbr', 'has_url','week_start_day_num','month_week_start','Year','month_year', 'Duration']].groupby(['Weekday_abbr','Year','month_abbr','month_year','session_date','has_url','week_start_day_num','month_week_start'], as_index=False).sum()
        
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
        Logger(session.ns)
        df_365 = df_365_stage_1()
        df_365 = df_365[df_365['Song'].notna()]
        df_365 = df_365.groupby(['Song Type','Song','Composer','Arranger'], as_index=False)['Duration'].sum()
        df_365['Minutes'] = df_365['Duration']%60
        df_365['Hours'] = (df_365['Duration']/60).apply(math.floor)
        df_365['Duration']=df_365['Duration']/60
        df_365 = df_365.sort_values('Duration', ascending=True)
        return df_365

    @render_widget
    def last_year_bar_chart():
        Logger(session.ns)
        df_365_songs = lastYearSongTransform()
        num_bars = len(list(df_365_songs['Song']))
        custom_data = [
            [composer, arranger, hours, minutes] for composer, arranger, hours, minutes in zip(
                list(df_365_songs['Composer']),
                list(df_365_songs['Arranger']),
                list(df_365_songs['Hours']),
                list(df_365_songs['Minutes']))
        ]

        
        fig = go.Figure(go.Bar(
            x=df_365_songs['Duration'], 
            y=[df_365_songs['Song Type'],df_365_songs['Song']], 
            orientation='h',
            marker=dict(cornerradius=30),         
            customdata=custom_data
        ))
        fig.update_traces(
            #width=.3,
            marker_color="#03A9F4",
            hovertemplate="""
                <b>Song:</b> %{y}<br>
                <b>Composer:</b> %{customdata[0]}<br>
                <b>Arranger:</b> %{customdata[1]}<br>
                <b>Total Practice Time:</b> %{customdata[2]} Hours, %{customdata[3]} Minutes
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
            
            height=50+(num_bars*20),
            plot_bgcolor="rgba(0, 0, 0, 0)",

            #Axis Label Style
            yaxis_tickfont=dict(size=14),
            

            # Tooltip Styling
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Garamond",
                bordercolor="black",
                align="left"
            ),
        )              
        fig.update_xaxes(title_text='Practice Time (Hours)')
        #fig.update_yaxes(ticklabelposition='outside top')
        fig.layout.xaxis.fixedrange = True
        fig.layout.yaxis.fixedrange = True

        figWidget = go.FigureWidget(fig)
        return figWidget



    @render_widget
    def last_week_bar_chart():
        Logger(session.ns)
        df_last_week = sessionNotesTransform()
        df_bar_summary = df_last_week.groupby('Song',as_index=False)[['Duration']].sum()
        num_bars = len(list(df_bar_summary['Song']))
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
            
            # Axis Label Size
            yaxis_tickfont=dict(size=14),
            #label = dict(yanchor='top'),

            height=50+(num_bars*20),
            plot_bgcolor="rgba(0, 0, 0, 0)",

            # Bar gap styling
            barmode='group',
            bargap=0.2,
            bargroupgap=0.0,

            # Tooltip Styling
            hoverlabel=dict(
                bgcolor="white",
                font_size=12,
                font_family="Garamond",
                bordercolor="black",
                align="left"
            ),
        )
        fig.update_xaxes(title_text='Practice Time (Minutes)')
        fig.layout.xaxis.fixedrange = True
        fig.layout.yaxis.fixedrange = True

        figWidget = go.FigureWidget(fig)
        return figWidget

    @render_widget
    def waffle_chart():
        Logger(session.ns)
        ret_dict = heatMapDataTranform()
        num_columns = len(ret_dict['Week Names'][0])
        print(num_columns)
        # add subplot here for year as stacked bar

        fig = go.Figure(
            go.Heatmap(
                x=ret_dict['Week Names'],
                y=ret_dict['Weekday Names'],
                z=ret_dict['Daily Practice Durations Grid'],     
                customdata=np.stack((
                    ret_dict['customdata'][0], # datetimes
                    ret_dict['customdata'][1], # Dates formatted as strings
                    ret_dict['customdata'][2] # '*' character for those marks that have videos
                    ), axis=-1),
                
                text=ret_dict['customdata'][2],
                texttemplate="%{text}",
                textfont={'size':14},
                #hovertemplate='Date: %{customdata[1]}<br>Duration (Minutes): %{z}',           
                
                # Tooltip Styling
                hoverlabel=dict(
                    bgcolor="white",
                    font_size=12,
                    font_family="Garamond",
                    bordercolor="black",
                    align="left"
                ),
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
        fig.update_traces(
            hovertemplate="""
                <b>Date:</b> %{customdata[1]}<br>
                <b>Total Duration (Minutes):</b> %{z}<br>
                <extra></extra>
            """,
        )  

        fig.update_layout(
            margin=dict(t=42, b=0, l=0, r=0),
            
            title=dict(text="Daily Practice Time (Past Year)",font=dict(size=30, color="#FFF8DC"),yanchor='bottom', yref='paper'),
            xaxis_side='bottom',
            xaxis_dtick=1, 
            
            # Main plot styling
            font_family='garamond',            
            font_color='#Ff9b15',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            
            xaxis_tickfont=dict(size=14),
            yaxis_tickfont=dict(size=14),

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

        df_day = reactive.value(pd.DataFrame())

        @render.data_frame
        def sessionNotesModalTable():
            Logger(session.ns)
            df_out = df_day()
            df_out = df_out.drop(['index','Session Date'],axis=1,errors='ignore')
            df_out = df_out[['Song','Notes','Duration']]
            return render.DataTable(df_out, width="100%", height="250px", styles=[{'class':'dashboard-table'}])


        # register on_click event
        def heatmap_on_click(trace, points, selector):
            Logger(session.ns)
            print("Entering heatmap_on_click()")

            # Get the customdata that corresponds to the clicked trace
            heatmap_y= points.point_inds[0][0]
            heatmap_x= points.point_inds[0][1]
            duration = trace.z[heatmap_y][heatmap_x]
            if duration>0:
                customdata = trace.customdata[heatmap_y,heatmap_x]
                
                query_date = customdata[0]
                str_date = customdata[1]

                df_day_session = sessionNotesTransform(from_date=query_date, num_days=0)
                #df_day_session = add_URL_icon_to_session_table(df_day_session,"heatmap_on_click")
                df_day_session = df_day_session[['Song','Session Date','Notes','Duration','Video URL']]
                df_day.set(df_day_session.copy())
                video_urls = df_day_session['Video URL'].replace('',None).copy()
                video_urls = video_urls[video_urls.notna()]
  
                def format_as_iframe(url):
                    embed_url = url
                    embed_url = embed_url[0:embed_url.find('?')]
                    embed_url = embed_url.replace('https://youtu.be/','https://youtube.com/embed/')
                    return ui.div(ui.HTML(f"""<iframe width="434" height="245" src="{embed_url}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>""")).add_class("day-modal-video"),
    
                i = ui.modal(
                    ui.div(
                        ui.h3(f"Practice Session: {str_date}").add_class("modal-title-text"),
                        ui.modal_button(label=None, icon=icon_svg("x")).add_class("modal-close", prepend=True), #you don't need to add the 'fa-' in front of the icon name
                    ).add_class("modal-titlebar"),
                    ui.row(
                        ui.output_data_frame(id="sessionNotesModalTable").add_class('dashboard-table', prepend=True),
                        [format_as_iframe(this_url) for this_url in video_urls],
                        ),
                    easy_close=False,
                    footer=None,
                )
                ui.modal_show(i)
                
            print("Exiting heatmap_on_click()")
        
        figWidget.data[0].on_click(heatmap_on_click)
        return figWidget

app_dir = Path(__file__).parent
app = App(app_ui, server, debug=False, static_assets=app_dir / "www")
