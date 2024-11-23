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
df_arsenal = globals._df_arsenal

Logger = logger.FunctionLogger

@module.ui
def guitar_ui():
    """
    Module to handle UI for each guitar card
    """
    ret_val = ui.div(
        ui.output_text(id="guitar_make_model").add_class("chart-title").add_style('text-align:center;'),
        ui.output_image(id="guitar_image").add_class('guitar-card-image')
    ).add_class('guitar-card'),
    return ret_val[0]

@module.server
def guitar_server(input, output, session,guitar_id):
    """
    Module to handle logic for each guitar card
    """
    this_row = df_arsenal.loc[guitar_id]
    
    @render.image
    def guitar_image():
        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "www" / this_row['image_link']), "width":"100%"}
        return img
    
    @render.text
    def guitar_make_model():
        make = this_row['make']
        model = this_row['model']
        return f"{make} {model}"

@module.ui
def arsenal_ui():
    ret_val = ui.nav_panel("Acoustic Arsenal",
        ui.div(
            [guitar_ui(str(row))for row in df_arsenal.index],
            #ui.card(ui.output_image(id="no_guitar_image").add_class('guitar-card-image')).add_class('guitar-card'),
            id="arsenal_placeholder",
        ).add_class('flex-horizontal').add_style('flex-wrap:wrap; justify-content:center;'),

    ),
    return ret_val


@module.server
def arsenal_server(input, output, session):
    Logger(session.ns)

    for row in df_arsenal.index:
        guitar_server(str(row),row) # pass twice, first time is for namespace, second time is by value
    
    @render.image
    def yamaha_cg1():
        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "www" / "YAMAHA-CG101MS.jpg"), "width":"100%"}
        return img
    
    @render.image
    def yamaha_g245():
        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "www" / "YAMAHA-G245S.jpg"), "width":"100%"}
        return img


    @render.image
    def no_guitar_image():
        dir = Path(__file__).resolve().parent
        img: ImgData = {"src": str(dir / "www" / "no-guitar-image.jpg"), "width":"100%"}
        return img
