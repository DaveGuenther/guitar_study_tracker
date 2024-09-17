# Core
import pandas as pd

from shiny import ui, module, render, reactive

import database

def default_func():
    pass

class ShinyTableModel:

    id=None
    title=None
    db_table_model=None
    df_resolved=None
    input_form_columns=None
    summary_columns=None
    input_form_ui = None
    server_function=None
    lookup_table_data=None

    def __init__(self, id:str, title:str, db_table_model:database.DatabaseModel, df_resolved:pd.DataFrame, input_form_columns:list, summary_columns:list, input_form_ui=None, server_function=default_func, lookup_table_data={}):
        self.id=id
        self.title=title
        self.db_table_model=db_table_model
        self.df_resolved=df_resolved
        self.input_form_columns=input_form_columns
        self.summary_columns=summary_columns
        self.input_form_ui = input_form_ui
        self.server_function=server_function
        self.lookup_table_data=lookup_table_data

    def inputFormUI():
        pass

shiny_data_payload = {}

# Processing for Artist
df_raw_artist = database.artist_model.df_raw
input_form_ui = ui.row(
    ui.input_text(id="artist_name",label="Artist Name"),
    ui.output_text(id='artist_name_output')
)

def server_func():
    input_form_func('artist')

@module.server
def input_form_func(input, output, session):
    
    output_text = reactive.value('')
    
    @reactive.effect
    @reactive.event(input.btn_input_form_submit)
    def triggerInputFormSubmit():
        ui.modal_remove()
        output_text.set(input.artist_name())

    @render.text
    def artist_name_output():
        return output_text

shiny_data_payload['artist'] = ShinyTableModel('artist','Artist', database.artist_model,df_raw_artist,list(df_raw_artist.columns),list(df_raw_artist.columns),input_form_ui, server_func)

# Processing for Song
df_raw_song = database.song_model.df_raw
df_resolved_song = df_raw_song.merge(df_raw_artist, how='left', left_on='composer', right_on='id').drop(['composer','id_y'],axis=1).rename({'id_x':'id','name':'Composer'},axis=1)
df_resolved_song = df_resolved_song.merge(df_raw_artist, how='left', left_on='arranger', right_on='id').drop(['arranger','id_y'],axis=1).rename({'id_x':'id','name':'Arranger'},axis=1)
df_resolved_song['Start Date'] = pd.to_datetime(df_resolved_song['start_date']).dt.strftime("%m/%d/%Y")
df_resolved_song['Off Book Date'] = pd.to_datetime(df_resolved_song['off_book_date']).dt.strftime("%m/%d/%Y")
df_resolved_song['Play Ready Date'] = pd.to_datetime(df_resolved_song['play_ready_date']).dt.strftime("%m/%d/%Y")
df_resolved_song = df_resolved_song.rename({'title':'Title'},axis=1)
shiny_data_payload['song'] = ShinyTableModel('song','Song', database.song_model,df_resolved_song,list(df_raw_song.columns),['id','Title','Composer','Arranger','Start Date','Off Book Date','Play Ready Date'])

# Processing for Practice Session
df_raw_practice_sessions = database.session_model.df_raw
df_resolved_sessions = df_raw_practice_sessions.merge(df_resolved_song,how='left', left_on='l_song_id', right_on='id').drop(['l_song_id','id_y'],axis=1).rename({'id_x':'id'},axis=1)
df_resolved_sessions['Session Date'] = pd.to_datetime(df_resolved_sessions['session_date']).dt.strftime("%m/%d/%Y")
df_resolved_sessions = df_resolved_sessions.rename({'duration':'Duration','notes':'Notes','Title':'Song'},axis=1)
shiny_data_payload['practice_session'] = ShinyTableModel('practice_session','Practice Session', database.session_model,df_resolved_sessions,list(df_raw_practice_sessions.columns),['id','Session Date','Song','Duration','Notes'])


print("hi")