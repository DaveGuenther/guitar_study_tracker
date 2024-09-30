# Core
import pandas as pd
import os
from dotenv import load_dotenv

# Web/Visual frameworks
from shiny import App, ui, render, reactive, types, req, module

# App Specific Code
import orm # database models
from database import DatabaseSession, DatabaseModel
from data_processing import ArtistInputTableModel # contains processed data payloads for each modular table in this app (use data_processing.shiny_data_payload dictionary)
from table_navigator import ShinyFormTemplate

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

artist_input_table_model = ArtistInputTableModel(namespace_id = 'artist', 
                                            title="Artist", 
                                            db_table_model=artist_model)

# Initialize artist input form
artist_form_template = ShinyFormTemplate('artist',artist_input_table_model)


app_ui = ui.page_fluid(

    ui.div(
        
        ui.h3("Guitar Study Tracker").add_style("text-align: center;"),
        ui.input_text(id='user',label="User Name:"),
        ui.input_password(id='password', label="Password:"),
        ui.input_action_button(id='btn_login',label='Login'),
        id="credentials_input",
    ),
    ui.div(id=f"nav_panels"),

)

def server(input, output, session):
    
    connected_to_db = reactive.value(False)
    #artist_input_table_model = reactive.value(None)
    #artist_form_template = reactive.value(None)

    @reactive.effect
    @reactive.event(input.btn_login, ignore_none=True, ignore_init=True)
    def btnLogin():

        if False==False:                
            with reactive.isolate():
                user_name=input.user()
                pw=input.password()



            # connect to database
            artist_model.connect(user_name, pw)

            # begin data processing in artist table navigator
            artist_input_table_model.processData()

            # remove user/pw screen
            ui.remove_ui(selector="#credentials_input")
            print("Login Clicked!!")
            # Insert the main tabs
            ui.insert_ui(
                selector=f"#nav_panels", 
                where="beforeBegin",
                ui= ui.page_navbar(
                    
                    ui.nav_panel("New Artist", "New Artist - Input Form",
                        artist_form_template.ui_call(),
                    ), 
                    #,
                    #ui.nav_panel("New Practice Session", "New Practice Session - Input Form",
                    #    table_navigator.nav_ui("practice_session", data_processing.shiny_data_payload['practice_session'])),            
                    #ui.nav_panel("New Song", "New Song - Input Form",
                    #    table_navigator.nav_ui("song", data_processing.shiny_data_payload['song'])),

                        #table_navigator.nav_ui("artist", data_processing.shiny_data_payload['artist'])),
                    title="Guitar Study Tracker",
                    id="page",
                ),
            )

            connected_to_db.set(True)
            artist_form_template.server_call(input, output, server)
            

    #table_navigator.nav_server("practice_session", data_processing.shiny_data_payload['practice_session'])
    #table_navigator.nav_server("song", data_processing.shiny_data_payload['song'])
    #table_navigator.nav_server("artist", data_processing.shiny_data_payload['artist'])
    


app = App(app_ui, server, debug=True)
