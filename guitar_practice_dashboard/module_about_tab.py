# Core
from shiny import ui, module
from datetime import date
import pandas as pd

# Utility
import logger

# App Specific Code
import global_data
globals = global_data.GlobalData()

Logger = logger.FunctionLogger

@module.ui
def about_ui():
    ret_val = ui.nav_panel(
        "About",
        "About"
    ),
    return ret_val


@module.server
def about_server(input, output, session):
    Logger(session.ns)
    pass