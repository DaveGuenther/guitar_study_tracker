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
            
            ui.output_text(id="guitar_make_model1").add_class("chart-title").add_style('text-align:center;'),
            ui.tooltip(
                ui.output_image(id="guitar_image").add_class('guitar-card-image'),
                ui.div(
                    # Show Guitar Make/Model in one Line
                    ui.output_ui(id="guitar_make_model2"),
                    ui.HTML("<br>"),
                    
                    # Show Guitar Status in one Line
                    ui.output_ui(id="tooltip_status"),
                    ui.HTML("<br>"),

                    # Show Guitar Use Dates in one Line
                    ui.output_ui(id="tooltip_dates_used"),
                    ui.HTML("<br>"),

                    ui.div("Hours on Guitar:").add_class('guitar-tooltip-title'),
                    ui.output_text(id="tooltip_guitar_hours_used"),
                    ui.HTML("<br>"),

                    ui.div("Strings:").add_class('guitar-tooltip-title'),
                    ui.output_text(id="tooltip_strings_installed"),                    
                    ui.HTML("<br>"),
                    
                    ui.div("Strings Installed On:").add_class('guitar-tooltip-title'),
                    ui.output_text(id="tooltip_strings_install_date"),                                        
                    ui.HTML("<br>"),
                    
                    ui.div("Hours On Current Strings:").add_class('guitar-tooltip-title'),
                    ui.output_text(id="tooltip_string_hours_used"),
                    ui.HTML("<br>"),
                    ui.div("Estimated String Health:").add_class('guitar-tooltip-title'),
                    ui.output_text(id="tooltip_string_percent"),                    
                ).add_class('guitar-tooltip').add_style('width:400px !important;'),
                placement='auto',
            ).add_style('width:400px !important;'),
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
    def guitar_make_model1():
        make = this_row['make']
        model = this_row['model']
        return f"{make} {model}"  
    
    @render.ui
    def guitar_make_model2():
        make = this_row['make']
        model = this_row['model']
        return ui.HTML(f'<span class="guitar-tooltip-title">Make/Model: </span>{make} {model}')

    @render.ui
    def tooltip_status():
        status=None
        if this_row['date_retired']:
            status="Retired"
        else:
            status="Active"
        return ui.HTML(f'<span class="guitar-tooltip-title">Status: </span>{status}')

    @render.ui
    def tooltip_dates_used():
        start_date=this_row['date_added'].strftime("%d-%m-%Y")
        if this_row['date_retired']:
            end_date=this_row['date_retired']
        else:
            end_date="Present"
        dates_str = f'{start_date} - {end_date}'
        return ui.HTML(f'<span class="guitar-tooltip-title">Dates Used: </span>{dates_str}')
    


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
