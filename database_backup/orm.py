# Core
import os
from dotenv import load_dotenv

# Data Integration
from sqlalchemy import Column, Integer, Text, Date, Boolean
from sqlalchemy.schema import Table, MetaData
from sqlalchemy.orm import declarative_base

load_dotenv("variables.env")
schema=os.getenv("pg_schema")
if not schema:
    schema = 'main'

Base = declarative_base()
metadata = Base.metadata

# Build table models with pertinent columns
tbl_artist = Table(
    'artist',
    metadata,
    Column('id', Integer, nullable=False),
    Column('name', Text, nullable=False),
    schema=schema,
)

tbl_style = Table(
    'style',
    metadata,
    Column('id', Integer, nullable=False),
    Column('style', Text, nullable=False),
    schema=schema,
)

tbl_arrangement = Table(
    'arrangement',
    metadata,
    Column('id', Integer, nullable=False),
    Column('start_date', Date, nullable=True),
    Column('off_book_date', Date, nullable=True),
    Column('at_tempo_date', Date, nullable=True),
    Column('play_ready_date', Date, nullable=True),
    Column('song_id', Integer, nullable=False), # foreign key to song.id
    Column('arranger', Integer, nullable=True), # foreign key to artist.id (writers and arrangers can be the same person)
    Column('difficulty', Text, nullable=True),
    Column('sheet_music_link', Text, nullable=True), # Link to sheet music online or book where it's located
    Column('performance_link', Text, nullable=True), # This would be a particular performance that I heard of the arrangement that I really liked.  It will probably color my phrasing once I learn it..  :p
    schema=schema,
)

tbl_song = Table(
    'song',
    metadata,
    Column('id', Integer, nullable=False),
    Column('title', Text, nullable=False),
    Column('style_id', Text, nullable=True), # foreign key to style.id
    Column('composer_id', Integer, nullable=True), # foreign key to artist.id
    Column('song_type', Text, nullable=True),
    schema=schema,
)

tbl_practice_session = Table(
    'practice_session',
    metadata,
    Column('id', Integer, nullable=False),
    Column('session_date', Date, nullable=False),
    Column('duration', Integer, nullable=False),
    Column('guitar_id', Integer, nullable=False), # foreign key to guitar.id
    Column('l_arrangement_id', Integer, nullable=False), # foreign key to arrangement.id
    Column('notes', Text, nullable=True),
    Column('video_url', Text, nullable=True),
    Column('stage', Text, nullable=True),
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
    Column('string_set_id', Integer, nullable=False), # foreign key to string_set.id
    Column('image_link', Integer, nullable=True),
    Column('date_added', Date, nullable=True),
    Column('date_retired', Date, nullable=True),
    Column('strings_install_date', Date, nullable=True),
    Column('default_guitar',Boolean, nullable=True),
    schema=schema,
)

tbl_arrangement_goals = Table(
    'arrangement_goals',
    metadata,
    Column('id', Integer, nullable=False),
    Column('arrangement_id', Integer, nullable=False), # foreign key to arrangement.id
    Column('discovery_date', Date, nullable=False),
    Column('description', Text, nullable=True),
    schema=schema,
)

tbl_string_set = Table(
    'string_set',
    metadata,
    Column('id', Integer, nullable=False),
    Column('name', Text, nullable = False),
    Column('hyperlink', Text, nullable=True),
    Column('image_url', Text, nullable=True),
    schema=schema,
)

