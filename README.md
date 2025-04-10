# Guitar Study Tracker
This is a shiny hobby app for ([data entry](https://dave-j-guenther.shinyapps.io/guitar_tracker_data_entry/)) to a postgres database and ([visual dashboard](https://dave-j-guenther.shinyapps.io/guitar_study_tracker/)) hosted on shinyapps.io to track guitar study progress and communicate with my teacher.  Class diagrams in the docs/ folder are created with Dia Diagram Editor: http://dia-installer.de/.

## Clone a Local Dev Copy!
Run the following commands in order to clone the repo and run the shiny app locally using a SQLite data cache instead of a live connection to a SQL database.  You don't have to build your virtual environment in the guitar_study_tracker/guitar_practice_dashboard folder or guitar_study_tracker/data_entry_app folder, but I found tooling it this way made it easier to integrate with VS Code and deploy to the cloud.  Within VS Code, you can use "Open Folder" to navigate to either the guitar_practice_dashboard or data_entry_app folder as the root of the project.  This way your virtual env is automatically detected and path is correct to load the cached SQLite data cache when you use "Run Shiny App" context menu from app.py. 

The instructions below are just for the visual dashboard.  Configuring the data_entry_app to use the SQLite database for reading works fine, but writing against the local data cache isn't possible at this time due to the SQLite cache lacking an AUTO INCREMENT feature on each table's id column, unlike the live database.

### Windows
``` shell
git clone git@github.com:DaveGuenther/guitar_study_tracker.git
cd guitar_study_tracker/guitar_practice_dashboard
python -m venv .venv
source ./.venv/Scripts/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Linux
``` linux
git clone git@github.com:DaveGuenther/guitar_study_tracker.git
cd guitar_study_tracker/guitar_practice_dashboard
python -m venv .venv
source ./.venv/bin/activate
pip install --upgrade pip setuptools wheel
sudo apt install libpq-dev   # for ubuntu systems  This is needed to pip install psycopg2
pip install -r requirements.txt
```

## Run Shiny App
In order to run the shiny app locally simply use <code>shiny run app.py</code>.  If you wish to run it from within VS Code, use the Open Folder command in VS Codde as described above and navigate to guitar_study_tracker/guitar_practice-dashboard as the project folder.  If you set up the virtual environment in this folder, you should be able to open app.py and then use either <code>Run Shiny App</code> or <code>Debug Shiny App</code> form the VS Code transport.

## Integrate with a Live SQL Database
If you decide to integrate this dashboard with our own SQL database, have a look at the pdf diagram of the database schema before continuing with the steps below: <br>
<img width="415" alt="image" src="https://github.com/user-attachments/assets/f0f6adc5-cb16-41f0-9531-f41417775720" />
<br>
Create a file in the <code>/data_entry_app</code>, <code>/guitar_practice_dashboard</code>, and <code>/database_backup</code> directories called "variables.env" that contains key value pairs for environment variables that we want to load into our app (replace values below with actual database values):
``` text
# variables.env
pg_user='*****' # Read only password
pg_pw='*****' # Read only password
pg_host='****'
pg_port='***'
pg_dbname='***'
pg_schema='***'
```
For reference on what to put in the variables above, the SQL connect string in database.py looks like this: <code>connect_string = f'postgresql+psycopg2://{user}:{password}@{self.__host}:{self.__port}/{self.__dbname}'</code>

## Deploy Instructions
This assumes that you have used rsconnect to created a server connection name called "shinyapps-io".
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
This project is set up to use a SQLite local database 'local_guitar_data.db' in the event that the application is unable to locate the variables.env file needed to access the live PostgreSQL database.  Look in the /database_backup folder for more information about how the backup works.  I will periodically update the cache and post it to the repo.
