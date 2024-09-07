# guitar_study_tracker
Private Shiny web form for data entry and public (Shinyapps.io) dashboard to track progress and communicate with teacher

## Env Setup
### Data Entry App: .venv_wr
This virtual environment will be used when building the data entry form, which stores write credentials as environment variables for posting to a local Shiny server.
``` linux
virtualenv .venv_wr
source ./venv_wr/bin/activate
pip install --upgrade pip setuptools wheel
sudo apt install libpq-dev   # for ubuntu systems  This is needed to pip install psycopg2
pip install requirements.txt
```
Once complete, edit .venv_wr/bin/activate and set environment variables at the bottom of the file that will be used for read-write database connection: pg_user, pg_pw, pg_host, pg_port, pg_dbname, pg_schema

### Visual Dashboard: .venv_rd
This virtual environment will be used when building the dashboard, which stores read credentials as environment variables for posting to Shinyapps.io
``` linux
virtualenv .venv_wr
source ./venv_wr/bin/activate
pip install --upgrade pip setuptools wheel
sudo apt install libpq-dev   # for ubuntu systems  This is needed to pip install psycopg2
pip install requirements.txt
```
Once complete, edit .venv_wr/bin/activate and set environment variables at the bottom of the file that will be used for read-only database connection: pg_user, pg_pw, pg_host, pg_port, pg_dbname, pg_schema


## Deploy Instructions
### Data Entry App:
It's important to have shiny only create the packages needed to run the app and not an entire pip freeze (pip freeze has led to deployment errors where shinyapps.io cannot build the environment properly.  For this reason, a requirements.txt was generated in the root folder of the repo.  We'll use that to generate a manifest, which will place a trimmed down version of that requirements.txt file into the app directory automatically.  If you have adjusted the app source code and added new .py files or pip installed new packages, you'll need to regenerate the manifest.json.  To recreate the manifest file, delect the one in data_entry_app/ and then from the root level of the repo:
``` linux
rsconnect write-manifest shiny data_entry_app/
```

To deploy to shinyapps.io:
``` linux
rsconnect deploy shiny data_entry_app/ --name dave-j-guenther --title "test_db_app2" -E pg_user -E pg_pw -E pg_host -E pg_port -E pg_dbname -E pg_schema
```

### Visual Dashboard:
