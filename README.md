# guitar_study_tracker
Private Shiny web form for data entry and public (Shinyapps.io) dashboard to track progress and communicate with teacher

## Env Setup
### Data Entry App: .venv_wr
This virtual environment will be used when building the data entry form, which stores write credentials as environment variables for posting to a local Shiny server.
``` linux
virtualenv .venv_wr
source ./venv_wr/bin/activate
pip install --upgrade pip setuptools wheel
pip install requirements.txt
```
Once complete, edit .venv_wr/bin/activate and set environment variables at the bottom of the file that will be used for read-write database connection: pg_user, pg_pw, pg_host, pg_port, pg_dbname, pg_schema

### Visual Dashboard: .venv_rd
This virtual environment will be used when building the dashboard, which stores read credentials as environment variables for posting to Shinyapps.io
``` linux
virtualenv .venv_wr
source ./venv_wr/bin/activate
pip install --upgrade pip setuptools wheel
pip install requirements.txt
```
Once complete, edit .venv_wr/bin/activate and set environment variables at the bottom of the file that will be used for read-only database connection: pg_user, pg_pw, pg_host, pg_port, pg_dbname, pg_schema
