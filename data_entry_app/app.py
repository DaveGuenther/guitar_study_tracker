# Core
import pandas as pd

# Web/Visual frameworks
from shiny import App, ui, render, reactive, types, req, module

# Shiny App Specific
import data_processing # contains processed data payloads for each modular table in this app (use data_processing.shiny_data_payload dictionary)
import table_navigator


app_ui = ui.page_fluid(
    ui.page_navbar(
        ui.nav_panel("New Practice Session", "New Practice Session - Input Form",
            table_navigator.nav_ui("practice_session", data_processing.shiny_data_payload['practice_session'])),            
        ui.nav_panel("New Song", "New Song - Input Form",
            table_navigator.nav_ui("song", data_processing.shiny_data_payload['song'])),
        ui.nav_panel("New Artist", "New Artist - Input Form",
            table_navigator.nav_ui("artist", data_processing.shiny_data_payload['artist'])),
        title="Guitar Study Tracker",
        id="page",
    ),
    ui.output_ui('page_manager'),
)

def server(input, output, session):

    table_navigator.nav_server("practice_session", data_processing.shiny_data_payload['practice_session'])
    table_navigator.nav_server("song", data_processing.shiny_data_payload['song'])
    table_navigator.nav_server("artist", data_processing.shiny_data_payload['artist'])
        
app = App(app_ui, server)
