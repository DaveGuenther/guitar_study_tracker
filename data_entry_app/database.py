# Core
import os
import pandas as pd

# Data Integration
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

# App specific
import orm

# pull database location and credential information from env variables
user=os.environ["pg_user"]
password=os.environ["pg_pw"]
host=os.environ["pg_host"]
port=os.environ["pg_port"]
dbname=os.environ["pg_dbname"]
connect_string = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}'

# Connect to db and establish session
engine = create_engine(connect_string)
Session = sessionmaker(bind=engine)
session=Session()

# pull tables into dataframes using orm definitions

print(select(orm.tbl_song))
df_songs = pd.read_sql(select(orm.tbl_song), session.bind)
df_artists = pd.read_sql(select(orm.tbl_artist), session.bind)
df_practice_sessions = pd.read_sql(select(orm.tbl_practice_session), session.bind)
df_practice_sessions['Session Date'] = pd.to_datetime(df_practice_sessions['session_date']).dt.strftime("%m/%d/%Y")



df_summary_practice_sessions = df_practice_sessions.merge(df_songs, how='left', left_on='l_song_id', right_on='id').rename({'id_x':'id'},axis=1)[['id','Session Date','title']]
df_summary_songs = df_songs.merge(df_artists, how='left', left_on='composer', right_on='id')[['title','composer']]
df_summary_artists = df_artists[['name']]
