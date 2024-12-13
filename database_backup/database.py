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
    __host=None
    __port=None
    __dbname=None

    def __init__(self, host:str=None, port:str=None, dbname:str=None):
        self.__host = host
        self.__port = port
        self.__dbname = dbname

    def connect(self, user:str=None, password:str=None):
        if self.__host:
            connect_string = f'postgresql+psycopg2://{user}:{password}@{self.__host}:{self.__port}/{self.__dbname}'
        else:
            print("variables.env not detected...  Loading local sqllite datebase")
            connect_string=f'sqlite:///local_guitar_data.db'

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
    __read_only_acct=False
    df_raw = None
    def __init__(self, orm_model: Table, db_session: DatabaseSession):
        self.__session = db_session
        self.__orm = orm_model

    def connect(self, user:str, pw:str, read_only_acct:bool):
        self.__session.connect(user, pw)
        self.__read_only_acct=read_only_acct
        self.read()

    def read(self):
        """
        Performs the equivelant of a SELECT * operation from the database based on the model provided and stores the result in public df_raw class attribute
        """
        self.df_raw = self.__session.readTable(self.__orm)


    def update(self, df_row):
        row = df_row.iloc[0]
        row_id = row['id']
        row = row.drop('id',errors='ignore')
        row_data = {key:value for key, value in zip(row.keys(), row.values)}
        self.__session.updateRecord(self.__orm, row_id, row_data)
        self.read()

    def insert(self, df_row):
        row = df_row.iloc[0]
        row = row.drop('id',errors='ignore')
        row_data = {key:value for key, value in zip(row.keys(), row.values)}
        self.__session.insertRecord(self.__orm, row_data)
        self.read()

    def delete(self, df_row):
        row = df_row.iloc[0]
        row_id=row['id']
        self.__session.deleteRecord(self.__orm, row_id)

    def isReadOnly(self):
        return self.__read_only_acct
