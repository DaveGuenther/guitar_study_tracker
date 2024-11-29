# Core
from shiny import ui, module, reactive, render
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
        "Goals",
        ui.output_text_verbatim("browser_resolution").add_class('legend-font'),
        ui.div("Hi",
            ui.div("Side Bar",
                ui.div("Plate").add_class('one').add_style('min-height:80px;'),
                ui.div("Plate").add_class('one').add_style('min-height:80px;'),
                ui.div("Plate").add_class('one').add_style('min-height:80px;'),
                ui.div("Plate").add_class('one').add_style('min-height:80px;'),
            ).add_class('two flex-vertical').add_style('flex:1 1 auto;'),
            ui.div("Main Content Area").add_class('four').add_style('flex:1,1,auto;'),
        ).add_class('flex-horizontal three'),
        ui.row(
            ui.column(3,"Column",
                ui.card("Row").add_class('one'),
                ui.card("Row").add_class('one'),
                ui.card("Row").add_class('one'),
                ui.card("Row").add_class('one'),
                ui.card("Row").add_class('one'),
                ui.card("Row").add_class('one'),
                ui.card("Row").add_class('one'),
                ui.card("Row").add_class('one'),
            
            ).add_class('three'),
            ui.column(9,"HELLO!").add_class('two'),
        ),    

    ),
    return ret_val


@module.server
def goals_server(input, output, session, browser_res):
    Logger(session.ns)
    
    @render.text
    def browser_resolution():
        return f"Browser dimensions: {browser_res()}"