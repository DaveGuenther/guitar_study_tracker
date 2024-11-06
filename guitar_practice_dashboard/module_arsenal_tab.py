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
def arsenal_ui():
    ret_val = ui.nav_panel(
                    "Acoustic Arsenal",
                    "Acoustic Arsenal",
                    "-=Guitar=-",
                    "-=Current Strings=-",
                    "-=Strings Installed on=-",
                    "-=Play Time on Strings=-",

                ),

    return ret_val


@module.server
def arsenal_server(input, output, session):
    Logger(session.ns)
    pass
