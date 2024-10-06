# Core
import pandas as pd
import os
from dotenv import load_dotenv
import logging

# Web/Visual frameworks
from shiny import App, ui, render, reactive, types, req, module

# App Specific Code
import orm # database models
from database import DatabaseSession, DatabaseModel
from data_processing import ArtistInputTableModel, SongInputTableModel, SessionInputTableModel # contains processed data payloads for each modular table in this app (use data_processing.shiny_data_payload dictionary)
from table_navigator import ShinyFormTemplate

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
artist_model = DatabaseModel(orm.tbl_artist,pg_session)
song_model = DatabaseModel(orm.tbl_song, pg_session)
session_model = DatabaseModel(orm.tbl_practice_session, pg_session)

user_name = os.getenv('pg_user')
pw = os.getenv('pg_pw')

artist_model.connect(user_name, pw, True)
song_model.connect(user_name, pw, True)
session_model.connect(user_name, pw, True)

def processData(p_session, song, artist):
    print("Hello World")
    pass

processed_data = processData(session_model, song_model, artist_model)

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
    pass


app = App(app_ui, server, debug=True)
