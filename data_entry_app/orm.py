# Core
import os

# Data Integration
from sqlalchemy import Column, Integer, Text, Date
from sqlalchemy.schema import Table, MetaData
from sqlalchemy.orm import declarative_base

schema=os.environ["pg_schema"]

Base = declarative_base()
metadata = Base.metadata

# Build table models with pertinent columns
tbl_artist = Table(
    'artist',
    metadata,
    Column('id', Integer, nullable=False),
    Column('name', Text, nullable=True),
    schema=schema,
)

tbl_song = Table(
    'song',
    metadata,
    Column('id', Integer, nullable=False,),
    Column('start_date', Date, nullable=True),
    Column('off_book_date', Date, nullable=True ),
    Column('play_ready_date', Date, nullable=True),
    Column('title', Text, nullable=False),
    Column('composer', Integer, nullable=True), # foreign key to artist.id
    Column('arranger', Integer, nullable=True), # foreign key to artist.id (writers and arrangers can be the same person)
    schema=schema,
)

tbl_practice_session = Table(
    'practice_session',
    metadata,
    Column('id', Integer, nullable=False),
    Column('session_date', Date, nullable=False),
    Column('duration', Integer, nullable=False),
    Column('notes', Text, nullable=True),
    Column('l_song_id', Integer, nullable=True), # foreign key to song.id
    schema=schema,
)
