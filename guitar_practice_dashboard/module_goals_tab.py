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
def goals_ui():
    ret_val = ui.nav_panel(
        "Goals",
        "Goals"
    ),
    return ret_val


@module.server
def goals_server(input, output, session):
    Logger(session.ns)
    pass