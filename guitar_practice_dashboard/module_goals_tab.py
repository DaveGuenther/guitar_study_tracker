# Core
from shiny import ui, module, reactive, render
from datetime import date
import pandas as pd

# Utility
import logger

# App Specific Code
import global_data
globals = global_data.GlobalData()
df_goal_arrangements = globals.get_df_song_goals()
df_goal_songs = df_goal_arrangements.drop_duplicates('song_id', keep='first')[['song_id','Title','Composer','Style']]
Logger = logger.FunctionLogger

style_dict = {
    'Classical':['red','#cf0c0c'],
    'Baroque':['blue','#180ccf'],
    'Romantic':['green','#16ba00'],
    'Spanish':['purple','#9600f0'],
    #'Style':['yellow','#ecff00'],
    'Latin':['orange','#f78c00']
    }

def custom_categorical_legend(legend_id, categories={'One':'red','Two':'Green','Three':'blue'},size=20, border_radius=5, border='1px solid black', title=None, title_padding='10px'):
    """
    
    """
    legend_id = str(legend_id)
    styles = """
        <style>
            .legend"""+legend_id+""" {
                display: flex;
                flex-wrap: wrap;
                align-items: center;
            }

            .legend-title"""+legend_id+""" {
                margin-right: """+title_padding+"""
                
            }

            .legend-item"""+legend_id+""" {
                display: flex;
                align-items: center;
                margin-right: 10px;
                
            }

            .legend-color"""+legend_id+""" {
                width: """+str(size)+"""px;
                height: """+str(size)+"""px;
                border: """+border+""";
                margin-right: 5px;
                border-radius: """+str(border_radius)+"""px;
            }
        </style>
        """
    legend = """
        <div class="legend"""+legend_id+"""">
        """
    if title:
        legend = legend+ """
            <div class="legend-title"""+legend_id+f"""">
                <span>{title}</span>
            </div>
            """

    for category, color in zip(categories.keys(), categories.values()):
        legend_item="""
            <div class="legend-item"""+legend_id+"""">
                <div class="legend-color"""+legend_id+"""" style="background-color: """+color+""";"></div>
                <span>"""+category+"""</span>
            </div>
            """
        legend+=legend_item
    legend+="""
        </div>
        """
    return styles+legend


@module.ui
def arrangement_details_card_ui(arr_id):
    ret_val = ui.card(
        ui.div("Arranger:").add_class('goal-main-content-title'),
        ui.output_text(id='txtArranger').add_class('goal-main-content-body'),
        ui.div("Difficulty:").add_class('goal-main-content-title'),
        ui.output_text(id='txtDifficulty').add_class('goal-main-content-body'),
        ui.div("Discovery Date:").add_class('goal-main-content-title'),
        ui.output_text(id='txtDiscoveryDate').add_class('goal-main-content-body'),
        ui.div("Arrangement Description:").add_class('goal-main-content-title'),
        ui.output_text(id='txtWhyThisSong').add_class('goal-main-content-body'),   
        ui.div("Sheet Music Link:").add_class('goal-main-content-title'),
        ui.output_ui(id='txtSheetMusicLink').add_class('goal-main-content-body'), 
        ui.div("Inspirational Video Link:").add_class('goal-main-content-title'),
        ui.output_ui(id='txtInspirationalVideoLink').add_class('goal-main-content-body'),                  
    ).add_class('dashboard-card'),
    return ret_val

@module.server
def arrangement_details_card_server(input, output, session, arr_id):

    @reactive.calc
    def get_arr_record_from_id():
        return df_goal_arrangements[df_goal_arrangements['id']==arr_id].iloc[0]

    @render.text
    def txtArranger():
        ret_val = get_arr_record_from_id()['Arranger']
        return ret_val

    @render.text
    def txtDifficulty():
        ret_val = get_arr_record_from_id()['Difficulty']
        return ret_val

    @render.text
    def txtWhyThisSong():
        ret_val = get_arr_record_from_id()['Description']
        return ret_val
    
    @render.text
    def txtDiscoveryDate():
        ret_val = get_arr_record_from_id()['Discovery Date'].strftime("%m-%d-%Y")
        return ret_val  

    @render.ui
    def txtInspirationalVideoLink():
        ret_val = "None"
        embed_url = get_arr_record_from_id()['Performance Link']
        if embed_url:
            embed_url = embed_url[0:embed_url.find('?')]
            embed_url = embed_url.replace('https://youtu.be/','https://youtube.com/embed/')
            ret_val = ui.div(ui.HTML(f"""<iframe src="{embed_url}" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>""")).add_class("day-modal-video"),
        return ret_val
    
    @render.ui
    def txtSheetMusicLink():
        ret_val = "None"
        embed_url = get_arr_record_from_id()['Sheet Music Link']
        if embed_url:
            ret_val = ui.HTML(f"""<a href="{embed_url}">{embed_url}</a>""")
        return ret_val

@module.ui
def goal_song_summary_card_ui(song_name, composer, style):
    plaque_color = style_dict[style][0]
    return ui.input_action_button(
        id='btn_song', 
        label=ui.div(              
            ui.div(
                ui.div(
                    f"{song_name}",
                    ui.br(),
                    f"{composer}",
                ),
            ).add_class(f"{plaque_color}-goal-plaque"),
        ).add_class('goal-plaque'),
    ).add_style('width:100%; border-style: none;'),

@module.server
def goal_song_summary_card_server(input, output, session, song_id, selected_song_id):

    @reactive.effect
    @reactive.event(input.btn_song)
    def set_selected_song():
        selected_song_id.set(song_id)

@module.ui
def goal_song_details_ui():
    ret_val=None
    ret_val =  ui.card(
        ui.div("Name:").add_class('goal-main-content-title'),
        ui.output_text(id='txtName').add_class('goal-main-content-body'),
        ui.div("Style:").add_class('goal-main-content-title'),
        ui.output_text(id='txtStyle').add_class('goal-main-content-body'),
        ui.div("Composer:").add_class('goal-main-content-title'),
        ui.output_text(id='txtComposer').add_class('goal-main-content-body'),
    ).add_class('dashboard-card'),
    return ret_val

@module.server
def goal_song_details_server(input, output, session, song_id):
    
    @reactive.calc
    def get_song_record_from_id():
        return df_goal_songs[df_goal_songs['song_id']==song_id].iloc[0]

    @render.text
    def txtName():
        ret_val = None
        if song_id:
            ret_val = get_song_record_from_id()['Title']
        return ret_val

    @render.text
    def txtStyle():
        ret_val = None
        if song_id:
            ret_val = get_song_record_from_id()['Style']
        return ret_val        

    @render.text
    def txtComposer():
        ret_val = None
        if song_id:        
            ret_val = get_song_record_from_id()['Composer']
        return ret_val



@module.ui
def goals_ui():
    ret_val = ui.nav_panel(
        "Goals",
        ui.div(
            ui.div(
                id='goals_tab-dynamic-ui-placeholder' # styling limits to 1200px wide
            ).add_class('stretch-vertical-height'),
        ).add_class('goal-flex-container'), # center content on screen
        value='goal-main-tab-panel',
    )
    return ret_val


@module.server
def goals_server(input, output, session, browser_res):
    Logger(session.ns)
    
    # state info about what is currently selected
    selected_song=reactive.value(None)

    #set up server modules for wide-view server cards
    [goal_song_summary_card_server(id='wide_'+str(song_id), song_id=str(song_id), selected_song_id=selected_song) for song_id in df_goal_arrangements['song_id'].unique()]

    #set up server modules for song detail cards
    [goal_song_details_server(id=song_id, song_id=song_id) for song_id in df_goal_arrangements['song_id'].unique()]

    #set up server modules for arrangement cards for each song (some songs have multiple arrangements)
    [arrangement_details_card_server(f"song{song_id}_arr{arr_id}_", arr_id) for song_id, arr_id in zip(df_goal_arrangements['song_id'], df_goal_arrangements['id'])]


    @render.text
    def style_legend():
        category_colors = {key:value[1] for key,value in zip(style_dict.keys(), style_dict.values())}
        legend_id = str(globals.get_legend_id())
        legend = custom_categorical_legend(legend_id, category_colors, title="Style: ")
        ret_val = legend
        return ret_val
    
    def main_text_side_panel(non_reactive_selected_song):
        ret_val = None
        if non_reactive_selected_song:
            style=df_goal_arrangements[df_goal_arrangements['song_id']==non_reactive_selected_song].iloc[0]['Style']
            plaque_color = style_dict[style][1]
            ret_val = ui.div(
                ui.div(
                    ui.div().add_class('song-style-colored-bar').add_style(f'background-color:{plaque_color};'),
                ).add_class('flex-horizontal'),
                ui.h3("About This Song:"),
                goal_song_details_ui(non_reactive_selected_song),
                ui.h3("Arrangements:"),
                [arrangement_details_card_ui(f"song{non_reactive_selected_song}_arr{arr_id}_", arr_id) for arr_id in df_goal_arrangements[df_goal_arrangements['song_id']==non_reactive_selected_song]['id']],
                ui.div(
                    ui.div().add_class('song-style-colored-bar').add_style(f'background-color:{plaque_color};'),
                ).add_class('flex-horizontal'),
            )
        return ret_val     

    def make_accordion_panels():
        ret_val = []
        for song_id in df_goal_songs['song_id']:
            row = df_goal_songs[df_goal_songs['song_id']==song_id].iloc[0]  ##  Needs lots of fixing
            plaque_style =style_dict[row['Style']][0]
            ret_val.append(
                
                ui.accordion_panel(
                        ui.div(
                            ui.div(              
                                ui.div(
                                    ui.div(
                                        row['Title'],
                                        ui.br(),
                                        row['Composer'],
                                    ),
                                ).add_class(f"{plaque_style}-goal-plaque"),
                            ).add_class('goal-plaque'),
                        ).add_style('width:100%; border-style: none;'),
                    main_text_side_panel(song_id),
                    value=row['song_id'],
                )
            )
        return ret_val

    @reactive.effect
    @reactive.event(browser_res, selected_song)
    def render_body():
        #print(browser_res())
        if browser_res()[0]>=677:
            ui.remove_ui("#goals_tab-wide-ui-placeholder")
            ui.remove_ui("#goals_tab-narrow-ui-placeholder")
            ui.insert_ui(
                selector=f"#goals_tab-dynamic-ui-placeholder", 
                where="afterBegin", # nest inside 'dynamic-ui-placeholder' element
                ui= ui.div(
                    ui.row(
                        ui.column(5,
                            ui.div(
                                ui.div().add_class('flex-blank'),
                                ui.output_ui(id='style_legend').add_class('legend-font').add_style('display:inline;'),
                                ui.div().add_class('flex-blank'),
                        ).add_class('flex-horizontal'),
                            [goal_song_summary_card_ui(id='wide_'+str(song_id), song_name=song_name, composer=composer, style=style) for song_id, song_name, composer, style in zip(df_goal_songs['song_id'],df_goal_songs['Title'],df_goal_songs['Composer'], df_goal_songs['Style'])],                  
                        ).add_class("wood-column"),
                        ui.column(7,
                            main_text_side_panel(selected_song()),
                        ),
                    ),#.add_style('height:100vh;'),
                    id='goals_tab-wide-ui-placeholder'
                ),#.add_class('stretch-vertical-height'),
            )
        else:
            ui.remove_ui("#goals_tab-narrow-ui-placeholder")
            ui.remove_ui("#goals_tab-wide-ui-placeholder")
            ui.insert_ui(
                selector=f"#goals_tab-dynamic-ui-placeholder", 
                where="afterBegin", # nest inside 'dynamic-ui-placeholder' element
                ui= ui.div(
                    ui.div(
                        ui.div(
                            ui.div().add_class('flex-blank'),
                            ui.output_ui(id='style_legend').add_class('legend-font').add_style('display:inline;'),
                            ui.div().add_class('flex-blank'),
                        ).add_class('flex-horizontal'),
                        ui.accordion(*make_accordion_panels(), id="acc_single", multiple=False),
                        
                    ).add_class('wood-column'),  
                    id='goals_tab-narrow-ui-placeholder'               
                ),#.add_style('height: 100vh;'),
            )
