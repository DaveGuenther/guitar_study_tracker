# Core

from datetime import date
import pandas as pd

# Utility
import logger

# Web/Visual frameworks
from shiny import ui, module
import plotly.graph_objects as go
from shinywidgets import output_widget, render_widget, render_plotly

# App Specific Code
import global_data
globals = global_data.GlobalData()

Logger = logger.FunctionLogger


df_sessions = globals.get_df_sessions()

def timestamp_to_date(this_timestamp: pd._libs.tslibs.timestamps._Timestamp):
    return date(this_timestamp.year, this_timestamp.month, this_timestamp.day)

@module.ui
def career_ui():

    def filter_shelf(df):
        return ui.div(
            ui.input_date_range(
                id='daterange',
                label='Date Range',
                start=timestamp_to_date(df['session_date'].min()),
                end=timestamp_to_date(df['session_date'].max()),
            ),
        )
    
    ret_val = ui.nav_panel("Career",
        "Career",
        ui.sidebar(
            ui.h4("Filters"),
            filter_shelf(df_sessions),
            width=300,
        ),
        ui.card(
            output_widget(id='song_grindage_chart')
        ).add_class('dashboard-card'),
        ui.row(
            ui.column(3,
                ui.card(
                    ui.h4("Avg. Practice Time/Day"),

                ),
            ),
            ui.column(2,
                ui.card(
                    ui.h4("Longest Practice Streak"),

                ),                        

            ),
            ui.column(2,
                ui.card(
                    ui.h4("Longest Session"),

                ),
            ),
            ui.column(3,
                ui.card(
                    ui.h4("Total Career Practice Time"),

                ),
            ),
            ui.column(2,
                ui.card(
                    ui.h4("Year:"),

                ),
            ),                                                                                                
        ),
    )

    return ret_val

@module.server
def career_server(input, output, session):
    Logger(session.ns)

    @render_widget
    def song_grindage_chart():
        df_grindage_data = df_sessions.groupby(['l_song_id'])
    
        