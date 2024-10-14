from shiny import ui
from datetime import datetime, date 
import pandas

def timestamp_to_date(this_timestamp: pandas._libs.tslibs.timestamps._Timestamp):
    return date(this_timestamp.year, this_timestamp.month, this_timestamp.day)



def filter_shelf(df):
    return ui.div(
        ui.input_date_range(
            id='daterange',
            label='Date Range',
            start=timestamp_to_date(df['session_date'].min()),
            end=timestamp_to_date(df['session_date'].max()),
        ),
    )