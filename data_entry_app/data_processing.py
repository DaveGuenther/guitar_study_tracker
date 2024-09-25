# Core
import pandas as pd
from abc import ABC, abstractmethod
from shiny import ui, module, render, reactive

import database

def default_func():
    pass

class ShinyInputTableModel(ABC):
    """
    This class will make use of DatabaseTableModels to establish more complete table representation for user form input (including where necessary bringing in lookup tables to resolve lookup ids in the primary table).  It also contains specific UI components required for the inpurt form modal.
    """

    _namespace_id=None
    _title=None
    _db_table_model=None
    df_summary=None
    
    def __init__(self, namespace_id:str, title:str, db_table_model:database.DatabaseModel):
        self._namespace_id=namespace_id
        self._title=title
        self._db_table_model=db_table_model
        self._processData()

    @abstractmethod
    def _processData():
        """
        This handles form specific data processing code needed to format column names or resolve lookups
        """
        pass

    @abstractmethod
    def _ui_specific_code(self):
        """
        This is where the specific table fields for the form will show up including their lookups where necesary.  The appropriate module namespace is invokved by the time this ui code is run.
        """
        pass

    def ui_call(self):
        """
        This is the blanket parent modal code ui code that sets up the modal with cancel and submit buttons
        """
        @module.ui
        def ui_modal():
            input_form_modal = ui.modal(
                self._ui_specific_code(),
                ui.row(
                    ui.column(4, ui.input_action_button("btn_input_cancel","Cancel",width="100%")),
                    ui.column(4),
                    ui.column(4, ui.input_action_button("btn_input_form_submit", "Submit", width="100%")),
                ),
                title=f"Input Form - New {self._title}",
                easy_close=True,
                footer=None,
            )
            return ui.modal_show(input_form_modal)

        return ui_modal(self._namespace_id)

    @abstractmethod
    def server_call(self, input, output, session):
        pass

class ArtistInputTableModel(ShinyInputTableModel):    

    def _processData(self):
        self.df_summary = self._db_table_model.df_raw.rename({'name':'Artist'},axis=1)

    def _ui_specific_code(self):
        """
        Artist Modal Form code goes here
        """
        return ui.row(
            ui.input_text(id="name",label=f"{self._title} Name"),
            ui.output_text(id='name_output'),
        ),

    def server_call(self, input, output, session):
        @module.server
        def input_form_func(input, output, session):

            output_text = reactive.value('')
            
            @reactive.effect
            @reactive.event(input.btn_input_form_submit, ignore_init=False, ignore_none=False)
            def triggerInputFormSubmit():
                #ui.modal_remove()
                print(f"{self._title} Name!")
                output_text.set(input.name())

            @render.text
            def name_output():
                return output_text()
            

            @reactive.effect
            @reactive.event(input.btn_input_cancel)
            def triggerInputCancel():
                ui.modal_remove()

        input_form_func(self._namespace_id)

artist_input_table_model = ArtistInputTableModel(namespace_id = 'artist', 
                                                 title="Artist", 
                                                 db_table_model=database.artist_model)


shiny_data_payload = {}

# Processing for Artist
df_raw_artist = database.artist_model.df_raw
input_form_ui = ui.row(
    ui.input_text(id="artist_name",label="Artist Name"),
    ui.output_text(id='artist_name_output')
)

def ui_func():
    input_ui('artist')


def server_func():
    input_form_func('artist')

@module.ui
def input_ui():
    return ui.row(
    ui.input_text(id="artist_name",label="Artist Name"),
    ui.output_text(id='artist_name_output')
)

@module.server
def input_form_func(input, output, session):
    print("Form Processed")
    output_text = reactive.value('')
    
    @reactive.effect
    @reactive.event(input.btn_input_form_submit, ignore_init=False, ignore_none=False)
    def triggerInputFormSubmit():
        #ui.modal_remove()
        print("Artist Name!")
        output_text.set(input.artist_name())

    @render.text
    def artist_name_output():
        return output_text

#shiny_data_payload['artist'] = ShinyTableModel('artist','Artist', database.artist_model,df_raw_artist,list(df_raw_artist.columns),list(df_raw_artist.columns),input_form_ui, server_func, ui_func)

# Processing for Song
df_raw_song = database.song_model.df_raw
df_resolved_song = df_raw_song.merge(df_raw_artist, how='left', left_on='composer', right_on='id').drop(['composer','id_y'],axis=1).rename({'id_x':'id','name':'Composer'},axis=1)
df_resolved_song = df_resolved_song.merge(df_raw_artist, how='left', left_on='arranger', right_on='id').drop(['arranger','id_y'],axis=1).rename({'id_x':'id','name':'Arranger'},axis=1)
df_resolved_song['Start Date'] = pd.to_datetime(df_resolved_song['start_date']).dt.strftime("%m/%d/%Y")
df_resolved_song['Off Book Date'] = pd.to_datetime(df_resolved_song['off_book_date']).dt.strftime("%m/%d/%Y")
df_resolved_song['Play Ready Date'] = pd.to_datetime(df_resolved_song['play_ready_date']).dt.strftime("%m/%d/%Y")
df_resolved_song = df_resolved_song.rename({'title':'Title'},axis=1)
#shiny_data_payload['song'] = ShinyTableModel('song','Song', database.song_model,df_resolved_song,list(df_raw_song.columns),['id','Title','Composer','Arranger','Start Date','Off Book Date','Play Ready Date'])

# Processing for Practice Session
df_raw_practice_sessions = database.session_model.df_raw
df_resolved_sessions = df_raw_practice_sessions.merge(df_resolved_song,how='left', left_on='l_song_id', right_on='id').drop(['l_song_id','id_y'],axis=1).rename({'id_x':'id'},axis=1)
df_resolved_sessions['Session Date'] = pd.to_datetime(df_resolved_sessions['session_date']).dt.strftime("%m/%d/%Y")
df_resolved_sessions = df_resolved_sessions.rename({'duration':'Duration','notes':'Notes','Title':'Song'},axis=1)
#shiny_data_payload['practice_session'] = ShinyTableModel('practice_session','Practice Session', database.session_model,df_resolved_sessions,list(df_raw_practice_sessions.columns),['id','Session Date','Song','Duration','Notes'])


print("hi")