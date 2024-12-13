


#%%
from dotenv import load_dotenv
import os
import sqlite3

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


import orm # database models
import database 

user_name=None
pw=None

# %%
## Read back into dataframes
# Establish database session minus credentials
local_pg_session = database.DatabaseSession()

read_only_acct=True
local_artist_model = database.DatabaseModel(orm.tbl_artist,local_pg_session)
local_style_model = database.DatabaseModel(orm.tbl_style, local_pg_session)
local_song_model = database.DatabaseModel(orm.tbl_song, local_pg_session)
local_arrangement_model = database.DatabaseModel(orm.tbl_arrangement, local_pg_session)
local_session_model = database.DatabaseModel(orm.tbl_practice_session, local_pg_session)
local_string_set_model = database.DatabaseModel(orm.tbl_string_set, local_pg_session)
local_arrangement_goal_model = database.DatabaseModel(orm.tbl_arrangement_goals, local_pg_session)
local_guitar_model = database.DatabaseModel(orm.tbl_guitar, local_pg_session)

# connect to database
local_string_set_model.connect(user_name, pw, read_only_acct)
local_artist_model.connect(user_name, pw, read_only_acct)
local_style_model.connect(user_name, pw, read_only_acct)
local_song_model.connect(user_name, pw, read_only_acct)
local_arrangement_model.connect(user_name, pw, read_only_acct)
local_session_model.connect(user_name, pw, read_only_acct)
local_arrangement_goal_model.connect(user_name, pw, read_only_acct)
local_guitar_model.connect(user_name, pw, read_only_acct)


# %%

print()
print("Artist")
print(local_artist_model.df_raw.iloc[0])
print()
print("String Set")
print(local_string_set_model.df_raw.iloc[0])
print()
print("Style")
print(local_style_model.df_raw.iloc[0])
print()
print("Song")
print(local_song_model.df_raw.iloc[0])
print()
print("Arrangement")
print(local_arrangement_model.df_raw.iloc[0])
print()
print("Session")
print(local_session_model.df_raw.iloc[0])
print()
print("Arrangement Goal")
print(local_arrangement_goal_model.df_raw.iloc[0])
print()
print("Guitar")
print(local_guitar_model.df_raw.iloc[0])