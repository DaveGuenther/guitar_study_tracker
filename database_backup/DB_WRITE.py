#%%
from dotenv import load_dotenv
import os
import sqlite3

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


import orm # database models
import database 
print("Loading variables.env")
# pull database location and credential information from env variables
load_dotenv("variables.env")

# Establish database session minus credentials
remote_pg_session = database.DatabaseSession(
    os.getenv("pg_host"),
    os.getenv("pg_port"),
    os.getenv("pg_dbname")
    )

user_name = os.getenv("pg_user")
pw = os.getenv('pg_pw')
read_only_acct=True


#%%
###Connect to Remote PostgreSQL Database
print("Building object relational maps")
# Create object relational mappings for the three database tables
remote_artist_model = database.DatabaseModel(orm.tbl_artist,remote_pg_session)
remote_style_model = database.DatabaseModel(orm.tbl_style, remote_pg_session)
remote_song_model = database.DatabaseModel(orm.tbl_song, remote_pg_session)
remote_arrangement_model = database.DatabaseModel(orm.tbl_arrangement, remote_pg_session)
remote_session_model = database.DatabaseModel(orm.tbl_practice_session, remote_pg_session)
remote_string_set_model = database.DatabaseModel(orm.tbl_string_set, remote_pg_session)
remote_arrangement_goal_model = database.DatabaseModel(orm.tbl_arrangement_goals, remote_pg_session)
remote_guitar_model = database.DatabaseModel(orm.tbl_guitar, remote_pg_session)

#%%
# connect to database
print("Connecting to PostgreSQL Database and reading tables")
remote_string_set_model.connect(user_name, pw, read_only_acct)
remote_artist_model.connect(user_name, pw, read_only_acct)
remote_style_model.connect(user_name, pw, read_only_acct)
remote_song_model.connect(user_name, pw, read_only_acct)
remote_arrangement_model.connect(user_name, pw, read_only_acct)
remote_session_model.connect(user_name, pw, read_only_acct)
remote_arrangement_goal_model.connect(user_name, pw, read_only_acct)
remote_guitar_model.connect(user_name, pw, read_only_acct)


print("Opening local SQLite Database")
#%%
#### Create Local SQLite Database
engine = create_engine('sqlite:///local_guitar_data.db') 

Session = sessionmaker(bind=engine)
session=Session()

#%%
print("Printing data to local database")
# Write the DataFrame to the local SQLLite database
remote_string_set_model.df_raw.to_sql('string_set', engine, if_exists='replace', index=False)
remote_artist_model.df_raw.to_sql('artist', engine, if_exists='replace')
remote_style_model.df_raw.to_sql('style', engine, if_exists='replace')
remote_song_model.df_raw.to_sql('song', engine, if_exists='replace')
remote_arrangement_model.df_raw.to_sql('arrangement', engine, if_exists='replace')
remote_session_model.df_raw.to_sql('practice_session', engine, if_exists='replace')
remote_arrangement_goal_model.df_raw.to_sql('arrangement_goals', engine, if_exists='replace')
remote_guitar_model.df_raw.to_sql('guitar', engine, if_exists='replace')
print("Backup Complete!")