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
    _df_sessions=None
    _df_365=None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GlobalData, cls).__new__(cls)
        return cls._instance

    def __init__(self):

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
        
        self._df_sessions, self._df_365 = data_prep.processData(session_model, song_model, artist_model, style_model)

    def get_df_sessions(self):
        return self._df_sessions
    
    def get_df_365(self):
        return self._df_365
    