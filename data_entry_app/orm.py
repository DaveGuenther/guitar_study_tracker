# Core
import os
from dotenv import load_dotenv

# Data Integration
from sqlalchemy import Column, Integer, Text, Date
from sqlalchemy.schema import Table, MetaData
from sqlalchemy.orm import declarative_base

load_dotenv("variables.env")
schema=os.getenv("pg_schema")

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

tbl_style = Table(
    'style',
    metadata,
    Column('id', Integer, nullable=False),
    Column('style', Text, nullable=False),
    schema=schema,
)

tbl_song = Table(
    'song',
    metadata,
    Column('id', Integer, nullable=False,),
    Column('start_date', Date, nullable=True),
    Column('off_book_date', Date, nullable=True),
    Column('at_tempo_date', Date, nullable=True),
    Column('play_ready_date', Date, nullable=True),
    Column('title', Text, nullable=False),
    Column('style_id', Text, nullable=True), # foreign key to style.id
    Column('composer', Integer, nullable=True), # foreign key to artist.id
    Column('arranger', Integer, nullable=True), # foreign key to artist.id (writers and arrangers can be the same person)
    Column('song_type', Text, nullable=True),
    schema=schema,
)

tbl_practice_session = Table(
    'practice_session',
    metadata,
    Column('id', Integer, nullable=False),
    Column('session_date', Date, nullable=False),
    Column('duration', Integer, nullable=False),
    Column('notes', Text, nullable=True),
    Column('video_url', Text, nullable=True),
    Column('l_song_id', Integer, nullable=True), # foreign key to song.id
    schema=schema,
)

tbl_guitar = Table(
    'guitar',
    metadata,
    Column('id', Integer, nullable=False),
    Column('make', Text, nullable=False),
    Column('model', Text, nullable=False),
    Column('status', Text, nullable=False), # Temporary, Permanent, or Retired
    Column('about', Text, nullable=False),
    Column('image_link', Integer, nullable=True),
    Column('date_added', Date, nullable=True),
    Column('string_set_id', Integer, nullable=False),
    Column('date_retired', Date, nullable=True),
    schema=schema,
)
