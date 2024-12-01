# Core
from shiny import ui, module, reactive, render
from datetime import date
import pandas as pd

# Utility
import logger

# App Specific Code
import global_data
globals = global_data.GlobalData()
df_goal_songs = globals.get_df_song_goals()
Logger = logger.FunctionLogger

@module.ui
def goal_song_card_ui(song_name, composer, arranger):
    return ui.input_action_button(
        id='btn_song', 
        label=ui.div(
            f"{song_name}",
            ui.br(),
            f"{composer}",
            ui.br(),
            f"Arr: {arranger}",
        )
    ).add_class('green').add_style('width:100%;'),

@module.server
def goal_song_card_server(input, output, session, song_id, selected_song_id):

    @reactive.effect
    @reactive.event(input.btn_song)
    def set_selected_song():
        selected_song_id.set(song_id)


@module.ui
def goals_ui():
    ret_val = ui.nav_panel(
        "Goals",
        #ui.tags.link(href='styles.css', rel="stylesheet"),
        ui.div(
            ui.div(
                id='goals_tab-dynamic-ui-placeholder'
            ),
        ).add_class('flex-horizontal'),
    )
    return ret_val


@module.server
def goals_server(input, output, session, browser_res):
    Logger(session.ns)
    
    # state info about what is currently selected
    selected_song=reactive.value(None)

    #ser up server modules for widw-view server cards
    [goal_song_card_server(id='wide_'+str(song_id), song_id=str(song_id), selected_song_id=selected_song) for song_id in df_goal_songs['id']]

    @reactive.calc
    def main_text_side_panel():
        ret_val = None
        if selected_song():
            ret_val = ui.div(
                ui.h2("About This Song"),
                ui.div("Name:").add_class('goal-main-content-title'),
                ui.output_text(id='txtName').add_class('goal-main-content-body'),
                ui.div("Style:").add_class('goal-main-content-title'),
                ui.output_text(id='txtStyle').add_class('goal-main-content-body'),
                ui.div("Composer:").add_class('goal-main-content-title'),
                ui.output_text(id='txtComposer').add_class('goal-main-content-body'),
                ui.div("Arranger:").add_class('goal-main-content-title'),
                ui.output_text(id='txtArranger').add_class('goal-main-content-body'),
                ui.div("Discovery Date:").add_class('goal-main-content-title'),
                ui.output_text(id='txtDiscoveryDate').add_class('goal-main-content-body'),
                ui.div("Description:").add_class('goal-main-content-title'),
                ui.output_text(id='txtWhyThisSong').add_class('goal-main-content-body'),    
            )
        return ret_val     

    @reactive.effect
    @reactive.event(browser_res, selected_song)
    def render_body():
        print(browser_res())
        if browser_res()[0]>=677:
            ui.remove_ui("#goals_tab-wide-ui-placeholder")
            ui.remove_ui("#goals_tab-narrow-ui-placeholder")
            ui.insert_ui(
                selector=f"#goals_tab-dynamic-ui-placeholder", 
                where="afterBegin", # nest inside 'dynamic-ui-placeholder' element
                ui= ui.div(
                    ui.row(
                        ui.column(5,
                            [goal_song_card_ui(id='wide_'+str(song_id), song_name=song_name, composer=composer, arranger=arranger) for song_id, song_name, composer, arranger in zip(df_goal_songs['id'],df_goal_songs['Title'],df_goal_songs['Composer'],df_goal_songs['Arranger'])],                  
                        ),
                        ui.column(7,
                            main_text_side_panel(),
                        ),
                    ),
                    id='goals_tab-wide-ui-placeholder'
                )
            )
        else:
            ui.remove_ui("#goals_tab-narrow-ui-placeholder")
            ui.remove_ui("#goals_tab-wide-ui-placeholder")
            ui.insert_ui(
                selector=f"#goals_tab-dynamic-ui-placeholder", 
                where="afterBegin", # nest inside 'dynamic-ui-placeholder' element
                ui= ui.div(
                    #ui.accordion(*make_accordion_panels(), id="acc_single", multiple=False).add_class('green'),
                    id='goals_tab-narrow-ui-placeholder'
                )
            )

    @reactive.calc
    def get_song_record_from_id():
        return df_goal_songs[df_goal_songs['id']==selected_song()].iloc[0]


    @render.text
    def txtName():
        ret_val = None
        if selected_song():
            ret_val = get_song_record_from_id()['Title']
        return ret_val

    @render.text
    def txtStyle():
        ret_val = None
        if selected_song():
            ret_val = get_song_record_from_id()['Style']
        return ret_val        

    @render.text
    def txtComposer():
        ret_val = None
        if selected_song():        
            ret_val = get_song_record_from_id()['Composer']
        return ret_val

    @render.text
    def txtArranger():
        ret_val = None
        if selected_song():        
            ret_val = get_song_record_from_id()['Arranger']
        return ret_val

    @render.text
    def txtWhyThisSong():
        ret_val = None
        if selected_song():
            ret_val = get_song_record_from_id()['Description']
        return ret_val
    
    @render.text
    def txtDiscoveryDate():
        ret_val = None
        if selected_song():
            ret_val = get_song_record_from_id()['Discovery Date'].strftime("%m-%d-%Y")
        return ret_val    