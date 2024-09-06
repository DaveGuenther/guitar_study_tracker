from sqlalchemy import create_engine, text, inspect, select
from sqlalchemy.schema import Table, MetaData
import os

user=os.environ["pg_user"]
password=os.environ["pg_pw"]
host=os.environ["pg_host"]
port=os.environ["pg_port"]
dbname=os.environ["pg_dbname"]
connect_string = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}'
schema=os.environ["pg_schema"]

engine = create_engine(connect_string)

insp = inspect(engine)
print(insp.get_schema_names())
print(insp.get_table_names(schema))

