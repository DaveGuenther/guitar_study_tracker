# Core
from pathlib import Path

import pandas as pd



# Web/Visual frameworks
from shiny import App, ui, render, reactive, types, req, module
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from shinywidgets import output_widget, render_widget, render_plotly
from shiny.types import ImgData


# App Specific Code
import global_data
globals = global_data.GlobalData()

import module_sessions_tab
import module_career_tab
import module_arsenal_tab
import module_about_tab
import module_goals_tab
import logger

Logger = logger.FunctionLogger
Logger.setLogger(True) # turn off the shinylogger



app_ui = ui.page_fluid(
        ui.head_content(
            ui.tags.meta(property="og:image", content="https://i.imgur.com/Gep8lXT.png"),
        ),
        ui.tags.link(href='styles.css', rel="stylesheet"),
        ui.tags.link(href='flex.css', rel="stylesheet"),
        ui.div(
            ui.page_navbar(
                module_sessions_tab.sessions_ui("sessions_tab"),
                # Execute ui code for shiny modules
                module_career_tab.career_ui("career_tab"),
                module_goals_tab.goals_ui('goals_tab'),
                module_arsenal_tab.arsenal_ui("arsenal_tab"),
                module_about_tab.about_ui("about_tab"),
              
            id='main_nav_bar',     
            title="Guitar Study Tracker",
            ),
        ),
        title="Guitar Study Tracker"

)


def server(input, output, session):
    module_sessions_tab.sessions_server("sessions_tab")
    module_career_tab.career_server("career_tab")
    module_goals_tab.goals_server("goals_tab")
    module_arsenal_tab.arsenal_server("arsenal_tab")
    module_about_tab.about_server("about_tab")


app_dir = Path(__file__).parent
app = App(app_ui, server, debug=False, static_assets=app_dir / "www")
