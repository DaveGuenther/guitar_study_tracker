# Database Extract Tool

This folder contains code to extract all tables from the PostgreSQL database and save them to a local SQLite database using the same ORM code.  Generally in each of the shiny apps (data_entry_app and guitar_practice_dashboard) if the variables.env file that sits in the same folder as the app.py is missing, the database library will open the SQLite local cache instead.  This functionality is so that folks who are interested and clone this repo and stil have a working dashboard locally to play with - they don't need access to the live SQL database.

## Backup Instructions

1. Make sure you have the variables.env set up with access information to read from PostgreSQL database
2. Run DB_WRITE.py file to extract all table data from PostgreSQL and write to local_guitar_data.DB_WRITE
3. Copy .db file to guitar_study_tracker/guitar_practice_dashboard and guitar_study_tracker/data_entry_app and overwrite their contents

## Test Read Instructions
1. Be sure that variables.env is renamed or missing in this folder
2. Run DB_READ.py to force read behavior to SQLite.  Successful run should print out the first row of each table from the local database as a series
