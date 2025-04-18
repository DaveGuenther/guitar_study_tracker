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
from data_processing import ArtistInputTableModel, StyleInputTableModel, SongInputTableModel, ArrangementInputTableModel, SessionInputTableModel, StringSetInputTableModel, ArrangementGoalInputTableModel, GuitarInputTableModel # contains processed data payloads for each modular table in this app (use data_processing.shiny_data_payload dictionary)
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
style_model = DatabaseModel(orm.tbl_style, pg_session)
song_model = DatabaseModel(orm.tbl_song, pg_session)
arrangement_model = DatabaseModel(orm.tbl_arrangement, pg_session)
session_model = DatabaseModel(orm.tbl_practice_session, pg_session)
string_set_model = DatabaseModel(orm.tbl_string_set, pg_session)
arrangement_goal_model = DatabaseModel(orm.tbl_arrangement_goals, pg_session)
guitar_model = DatabaseModel(orm.tbl_guitar, pg_session)

# Establish schema specific table models (tying together their lookups)

string_set_input_table_model = StringSetInputTableModel(namespace_id = 'string_set',
                                                        title='String Set',
                                                        db_table_model=string_set_model)

artist_input_table_model = ArtistInputTableModel(namespace_id = 'artist', 
                                            title="Artist", 
                                            db_table_model=artist_model)

style_input_table_model = StyleInputTableModel(namespace_id = 'style',
                                               title='Style',
                                               db_table_model=style_model)

song_input_table_model = SongInputTableModel(namespace_id='song',
                                             title='Song',
                                             db_table_model=song_model,
                                             db_artist_model=artist_model, #required lookup
                                             db_style_model=style_model) #required lookup
                                             

arrangement_input_table_model = ArrangementInputTableModel(namespace_id = 'arrangement', 
                                            title="Arrangement", 
                                            db_table_model=arrangement_model,
                                            db_song_model=song_model, # required lookup
                                            db_artist_model=artist_model, #required lookup
                                            db_style_model=style_model) #required lookup

arrangement_goal_input_table_model = ArrangementGoalInputTableModel(namespace_id='arrangement_goal',
                                                      title="Arrangement Goals", 
                                                      db_table_model=arrangement_goal_model,
                                                      db_arrangement_model=arrangement_model, 
                                                      db_song_model=song_model, # required lookup
                                                      db_artist_model=artist_model)

guitar_input_table_model = GuitarInputTableModel(namespace_id='guitar',
                                                 title="Guitar",
                                                 db_table_model=guitar_model,
                                                 db_string_set_model=string_set_model)

session_input_table_model = SessionInputTableModel(namespace_id = 'session', 
                                            title="Session", 
                                            db_table_model=session_model,
                                            db_arrangement_model=arrangement_model, # required lookup
                                            db_song_model=song_model, # required lookup
                                            db_artist_model=artist_model, # required lookup
                                            db_guitar_model=guitar_model) # required lookup


# Initialize table navigator form
string_set_form_template = ShinyFormTemplate('string_set',string_set_input_table_model)
artist_form_template = ShinyFormTemplate('artist',artist_input_table_model)
style_form_template = ShinyFormTemplate('style',style_input_table_model)
song_form_template = ShinyFormTemplate('song',song_input_table_model)
arrangement_form_template = ShinyFormTemplate('arrangement',arrangement_input_table_model)
session_form_template = ShinyFormTemplate('session',session_input_table_model)
arrangement_goal_form_template = ShinyFormTemplate('arrangement_goal', arrangement_goal_input_table_model)
guitar_form_template = ShinyFormTemplate('guitar',guitar_input_table_model)

app_ui = ui.page_fluid(

    ui.div(
        
        ui.h3("Guitar Study Tracker").add_style("text-align: center;"),
        ui.input_text(id='user',label="User Name:"),
        ui.input_password(id='password', label="Password:"),
        ui.div("Logging in without credentials will use cached read-only credentials to the database."),
        ui.input_action_button(id='btn_login',label='Login'),
        id="credentials_input",
    ),
    ui.div(id=f"nav_panels"),

)

def dynamic_app_title(read_only_acct):
    if read_only_acct:
        return "Guitar Study Tracker (READ ONLY)"
    else:
        return "Guitar Study Tracker"

def server(input, output, session):
    
    connected_to_db = reactive.value(False)

    @reactive.effect
    @reactive.event(input.btn_login, ignore_none=True, ignore_init=True)
    def btnLogin():
             
        with reactive.isolate():
            user_name=input.user()
            pw=input.password()
            read_only_acct=False
            if (not user_name)&(not pw):
                print("Empty Username/PW, using read acct")
                user_name = os.getenv('pg_user')
                pw = os.getenv('pg_pw')
                read_only_acct=True

        # connect to database
        string_set_model.connect(user_name, pw, read_only_acct)
        artist_model.connect(user_name, pw, read_only_acct)
        style_model.connect(user_name, pw, read_only_acct)
        song_model.connect(user_name, pw, read_only_acct)
        arrangement_model.connect(user_name, pw, read_only_acct)
        session_model.connect(user_name, pw, read_only_acct)
        arrangement_goal_model.connect(user_name, pw, read_only_acct)
        guitar_model.connect(user_name, pw, read_only_acct)

        # begin data processing in artist table navigator
        string_set_input_table_model.processData()
        artist_input_table_model.processData()
        style_input_table_model.processData()
        song_input_table_model.processData()
        arrangement_input_table_model.processData()
        session_input_table_model.processData()
        arrangement_goal_input_table_model.processData()
        guitar_input_table_model.processData()

        # remove user/pw screen
        ui.remove_ui(selector="#credentials_input")

        # Insert the main tabs
        ui.insert_ui(
            selector=f"#nav_panels", 
            where="beforeBegin",
            ui= ui.page_navbar(
                # Execute ui code for shiny modules
                ui.nav_panel("Sessions", 
                    session_form_template.ui_call(),
                ), 

                ui.nav_panel("Songs",
                    song_form_template.ui_call(),
                ),

                ui.nav_panel("Arrangements",
                    arrangement_form_template.ui_call(),
                ),

                ui.nav_panel("Artists", 
                    artist_form_template.ui_call(),
                ),           

                ui.nav_panel("Arrangement Goals", 
                    arrangement_goal_form_template.ui_call(),
                ),                            

                ui.nav_panel("Music Styles", 
                    style_form_template.ui_call(),
                ),                    

                ui.nav_panel("Guitars", 
                    guitar_form_template.ui_call(),
                ),   

                ui.nav_panel("String Sets", 
                    string_set_form_template.ui_call(),
                ),               

                title=dynamic_app_title(read_only_acct),
                id="page",
            ),
        )

        connected_to_db.set(True)

        # Execute server code for shiny modules
        string_set_form_template.server_call(input, output, session)
        artist_form_template.server_call(input, output, session)
        style_form_template.server_call(input, output, session)
        song_form_template.server_call(input, output, session)
        arrangement_form_template.server_call(input, output, session)
        session_form_template.server_call(input, output, session)  
        arrangement_goal_form_template.server_call(input, output, session)  
        guitar_form_template.server_call(input, output, session)



app = App(app_ui, server, debug=False)
