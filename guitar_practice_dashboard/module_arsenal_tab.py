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

                    # Show Hours spent on Guitar
                    ui.output_ui(id="tooltip_guitar_hours_used"),
                    ui.HTML("<br>"),

                    # Show picture of strings with link to amazon page
                    ui.div("Strings Installed:").add_class('guitar-tooltip-title'),
                    ui.output_ui(id="tooltip_strings_installed"),
                    ui.HTML("<br>"),
                    
                    # Show String Install Date 
                    ui.output_ui(id="tooltip_strings_install_date"),
                    ui.HTML("<br>"),

                    # Show Hours used on Strings
                    ui.output_ui(id="tooltip_string_hours_used"),
                    ui.HTML("<br>"),

                    # Show String Health
                    ui.output_ui(id="tooltip_string_percent"),
                    ui.HTML("<br>"),

                    # Show picture of strings with link to amazon page
                    ui.div("About this Guitar:").add_class('guitar-tooltip-title'),
                    ui.output_ui(id="tooltip_about_guitar"),
                    ui.HTML("<br>"),

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
        start_date=this_row['date_added'].strftime("%m-%d-%Y")
        if this_row['date_retired']:
            end_date=this_row['date_retired'].strftime("%m-%d-%Y")
        else:
            end_date="Present"
        dates_str = f'{start_date} - {end_date}'
        return ui.HTML(f'<span class="guitar-tooltip-title">Dates Used: </span>{dates_str}')
    
    @render.ui
    def tooltip_guitar_hours_used():
        hours_on_guitar = int(this_row['hours_on_guitar']*10)/10
        return ui.HTML(f'<span class="guitar-tooltip-title">Hours on This Guitar: </span>{hours_on_guitar}')

    @render.ui
    def tooltip_strings_installed():
        string_name = this_row['name']
        img_link=this_row['image_url']
        hyper_link=this_row['hyperlink']
        return ui.div(
            ui.div(f'{string_name}').add_style("width:300px;"),
            ui.HTML(f'<a href="{hyper_link}" target="_blank"><img src="{img_link}" alt="{string_name}" style="width:100px;"></a>'),
        )

    @render.ui
    def tooltip_strings_install_date():
        install_date = this_row['strings_install_date'].strftime("%m-%d-%Y")
        days_on_strings = this_row['days_on_strings']
        return ui.HTML(f'<span class="guitar-tooltip-title">Strings Installed On: </span>{install_date} ({days_on_strings} days ago)')

    @render.ui
    def tooltip_string_hours_used():
        install_date = int(this_row['hours_on_strings']*10)/10
        return ui.HTML(f'<span class="guitar-tooltip-title">Hours On Current Strings: </span>{install_date}')

    @render.ui
    def tooltip_string_percent():
        this_row
        string_health = int(this_row['string_health']*100)
        color='green'
        if string_health<40:
            color='yellow'
        if string_health<20:
            color='red'
        days_left = this_row['expected_days_left']
        return ui.HTML(f'<span class="guitar-tooltip-title">String Health: </span><span style="font-weight:bolder;color:{color};">{string_health}%</span> (Estimated {days_left} days left)')

    @render.ui
    def tooltip_about_guitar():
        about_text= this_row['about']
        return ui.div(f'{about_text}').add_style("width:300px;")

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
