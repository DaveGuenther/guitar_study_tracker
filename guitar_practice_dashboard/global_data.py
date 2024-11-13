# Core
from dotenv import load_dotenv
import os

# App Specific Code
import orm # database models
from database import DatabaseSession, DatabaseModel
import data_prep


class GlobalData:
    """
    This is a singleton class intended to keep track of global non-reactive data that will be used by all the modules.
    """
    # used for singleton pattern
    _instance=None
    _df_sessions=None # General sessions data to understand time spent playing songs
    _df_365=None # Dataset used to build the waffle chart on the main page
    _df_song_grindage=None # Dataset that is used to build 

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalData, cls).__new__(cls)
            load_dotenv("variables.env")

            # Establish database session minus credentials
            pg_session = DatabaseSession(
                os.getenv("pg_host"),
                os.getenv("pg_port"),
                os.getenv("pg_dbname")
                )

            print(id(cls))

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
            
            cls._df_sessions, cls._df_365 = data_prep.processData(session_model, song_model, artist_model, style_model)
            cls._df_song_grindage = data_prep.processSongGrindageData(cls._df_sessions, session_model, song_model)

        return cls._instance

    def __init__(self):

        # pull database location and credential information from env variables
        print('Global Data Store Called')

    def get_df_sessions(self):
        return self._df_sessions
    
    def get_df_365(self):
        return self._df_365
    
    def get_df_song_grindage(self):
        return self._df_song_grindage
    
