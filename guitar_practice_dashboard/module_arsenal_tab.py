# Core
from datetime import date
import pandas as pd
from pathlib import Path

# Web/Visual frameworks
from shiny import ui, module, render
from shiny.types import ImgData

# Utility
import logger

# App Specific Code
import global_data
globals = global_data.GlobalData()

Logger = logger.FunctionLogger

@module.ui
def arsenal_ui():
    ret_val = ui.nav_panel("Acoustic Arsenal",
        ui.div(
            ui.card(ui.output_image(id="yamaha_cg1").add_class('guitar-card-image')).add_class('guitar-card'),
            ui.card(ui.output_image(id="no_guitar_image").add_class('guitar-card-image')).add_class('guitar-card'),

        ).add_class('flex-horizontal').add_style('flex-wrap:wrap; justify-content:center;'),

    ),

    return ret_val


@module.server
def arsenal_server(input, output, session):
    Logger(session.ns)
    
    @render.image
    def yamaha_cg1():
        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "www" / "YAMAHA-CG101MS.jpg"), "width":"100%"}
        return img
    
    @render.image
    def no_guitar_image():
        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "www" / "no-guitar-image.jpg"), "width":"100%"}
        return img
