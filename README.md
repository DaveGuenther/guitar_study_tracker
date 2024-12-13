# guitar_study_tracker
Public shiny app for data entry to a postgres database and public app with visual dashboard (Shinyapps.io) to track guitar study progress and communicate with my teacher.  Class diagrams in the docs/ folder are created with Dia Diagram Editor: http://dia-installer.de/.

## Env Setup
This virtual environment will be used when building the data entry form, which stores write credentials as environment variables for posting to a local Shiny server.
``` linux
python -m venv .venv
source ./venv_wr/bin/activate
pip install --upgrade pip setuptools wheel
sudo apt install libpq-dev   # for ubuntu systems  This is needed to pip install psycopg2
pip install requirements.txt
```
Once complete, create a file in the /data_entry_app, /guitar_practice_dashboard, and /database_backup directories called "variables.env" that contains key value pairs for environment variables that we want to load into our app (replace values below with actual database values):
``` text
pg_user='*****' # Read only password
pg_pw='*****' # Read only password
pg_host='****'
pg_port='***'
pg_dbname='***'
pg_schema='***'
```

## Deploy Instructions
### Data Entry App:
To deploy to shinyapps.io:
``` linux
rsconnect deploy shiny --new data_entry_app/ --name shinyapps-io --title "guitar_tracker_data_entry"
```

### Visual Dashboard:
To deploy to shinyapps.io:
``` linux
rsconnect deploy shiny --new guitar_practice_dashboard/ --name shinyapps-io --title "guitar_study_tracker"
```

## Database Backup Instructions
This project is set up to use a SQLite local database 'local_guitar_data.db' in the event that the application is unable to locate the variables.env file needed to access the live PostgreSQL database.  Look in the /database_backup folder for more information about how the backup works.
