# Core
import pandas as pd
import os
from dotenv import load_dotenv
import logging

# Web/Visual frameworks
from shiny import App, ui, render, reactive, types, req, module
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
                    output_widget(id='waffle_chart'),
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
        #prep for heatmap
        df_grouped = df_sessions[['Weekday_abbr','Week','Year', 'Duration']].groupby(['Weekday_abbr','Year','Week'], as_index=False).sum()
        df_grouped = df_grouped.sort_values(['Year','Week'])
        df_z = df_grouped.pivot(index=['Weekday_abbr'], columns=['Year','Week'])
        df_z = df_z.loc[['Sun','Mon','Tue','Wed','Thu','Fri','Sat'],]
        df_z = df_z.fillna('')
        z=[list(df_z.loc[wk_day,]) for wk_day in df_z.index]        
        x = list(df_z.T.index.levels[2].astype(int))
        y = list(df_z.index)    
        return x, y, z


    @render_widget
    def waffle_chart():
        x, y, z = heatMapDataTranform()
        fig = go.Figure(
            data=go.Heatmap(
                z=z,
                x=x,
                y=y,
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
                    thickness=40,


    )
            )   
        )
        figWidget = go.FigureWidget(fig)
        return figWidget




app = App(app_ui, server, debug=True)
