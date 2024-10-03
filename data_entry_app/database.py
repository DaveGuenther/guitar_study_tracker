# Core
import os
#from dotenv import load_dotenv
import pandas as pd

# Data Integration
from sqlalchemy import create_engine, select, insert, update, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.schema import Table

# App specific
import orm

class DatabaseSession:
    """
    This class manages the connection with PostgreSQL and contains the active database session and manages data transmission with the database.
    """
    __session=None

    def __init__(self, host:str, port:str, dbname:str):
        self.__host = host
        self.__port = port
        self.__dbname = dbname

    def connect(self, user:str, password:str):
        connect_string = f'postgresql+psycopg2://{user}:{password}@{self.__host}:{self.__port}/{self.__dbname}'

        # Connect to db and establish session
        engine = create_engine(connect_string)

        Session = sessionmaker(bind=engine)
        self.__session=Session()

    def readTable(self, model):
        """
        Selects all data from the defined table model and returns as a pd.DataFrame"""
        return pd.read_sql(select(model), self.__session.bind).copy()

    def updateRecord(self, model, row_id, row_data):
        """
        Given a single row dataframe, this will add a record to an existing table
        """
        row_id = int(row_id)
        stmt = update(model).where(model.c.id == row_id).values(row_data)
        self.__session.execute(stmt)
        self.__session.commit()

    def insertRecord(self, model, row_data):
        """
        Given a single row dataframe, this will add a record to an existing table
        """
        stmt = insert(model).values(row_data)
        self.__session.execute(stmt)
        self.__session.commit()

    def deleteRecord(self, model, row_id):
        stmt = delete(model).where(model.c.id == row_id)
        self.__session.execute(stmt)
        self.__session.commit()

class DatabaseModel:
    __session = None
    __orm = None
    df_raw = None
    def __init__(self, orm_model: Table, db_session: DatabaseSession):
        self.__session = db_session
        self.__orm = orm_model

    def connect(self, user:str, pw:str):
        self.__session.connect(user, pw)
        self.read()

    def read(self):
        """
        Performs the equivelant of a SELECT * operation from the database based on the model provided and stores the result in public df_raw class attribute
        """
        self.df_raw = self.__session.readTable(self.__orm)


    def update(self, df_row):
        row = df_row.loc[0]
        row_id = row['id']
        row = row.drop('id',errors='ignore')
        row_data = {key:value for key, value in zip(row.keys(), row.values)}
        self.__session.updateRecord(self.__orm, row_id, row_data)
        self.read()

    def insert(self, df_row):
        row = df_row.loc[0]
        row = row.drop('id',errors='ignore')
        row_data = {key:value for key, value in zip(row.keys(), row.values)}
        self.__session.insertRecord(self.__orm, row_data)
        self.read()

    def delete(self, df_row):
        row = df_row.loc[0]
        row_id=row['id']
        self.__session.deleteRecord(self.__orm, row_id)

# pull database location and credential information from env variables
#load_dotenv("variables.env")

#pg_session = DatabaseSession(
#    os.getenv("pg_user"),
#    os.getenv("pg_pw"),
#    os.getenv("pg_host"),
#    os.getenv("pg_port"),
#    os.getenv("pg_dbname")
#    )

#artist_model = DatabaseModel(orm.tbl_artist,pg_session)
#song_model = DatabaseModel(orm.tbl_song, pg_session)
#session_model = DatabaseModel(orm.tbl_practice_session, pg_session)


# pull tables into dataframes using orm definitions

#print(select(orm.tbl_song))
#df_songs = pd.read_sql(select(orm.tbl_song), session.bind)
#df_artists = pd.read_sql(select(orm.tbl_artist), session.bind)
#df_practice_sessions = pd.read_sql(select(orm.tbl_practice_session), session.bind)
#df_practice_sessions['Session Date'] = pd.to_datetime(df_practice_sessions['session_date']).dt.strftime("%m/%d/%Y")



#df_summary_practice_sessions = df_practice_sessions.merge(df_songs, how='left', left_on='l_song_id', right_on='id').rename({'id_x':'id'},axis=1)[['id','Session Date','title']]
#df_summary_songs = df_songs.merge(df_artists, how='left', left_on='composer', right_on='id').drop('composer',axis=1).rename({'id_x':'id','name':'composer'},axis=1)[['id','title','composer']]
#df_summary_artists = df_artists[['id','name']]

