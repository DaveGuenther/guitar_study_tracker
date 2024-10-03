# Core
import pandas as pd
import math
from abc import ABC, abstractmethod
from shiny import ui, module, render, reactive

import database

def default_func():
    pass

class ShinyInputTableModel(ABC):
    """
    This class will make use of DatabaseTableModels to establish more complete table representation for user form input (including where necessary bringing in lookup tables to resolve lookup ids in the primary table).  It also contains specific UI components required for the inpurt form modal.
    """

    _namespace_id=None # used as prefix for the shiny module (e.g. 'artist','song')
    _title=None # used for displaying in form titles in the shiny module (e.g. 'Artist','Song')
    _db_table_model=None # This object manages read/write access to the specific table itself (database model)
    df_summary=None # used to store the summarized view (with appropriate lookups resolved) that is provided to thje table navigator
    _df_selected_id = None # This is the selected row passed in from the table navigator

    @abstractmethod
    def processData():
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

    def ui_call(self, df_selected_id):
        """
        This is the blanket parent modal code ui code that sets up the modal with cancel and submit buttons
        """
        self._df_selected_id = df_selected_id
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
    def server_call(self, input, output, session, summary_df):
        pass

class ArtistInputTableModel(ShinyInputTableModel):    

    def __init__(self, namespace_id:str, title:str, db_table_model:database.DatabaseModel):
        self._namespace_id=namespace_id
        self._title=title
        self._db_table_model=db_table_model

    def processData(self):
        self.df_summary = self._db_table_model.df_raw.rename({'name':'Artist'},axis=1).copy()

    def __init_name(self):
        if self._df_selected_id:
            # provide initial value for the name field of the input form
            return str(self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['name'].values[0])
        else:
            return None
    
    def _ui_specific_code(self):
        """
        Artist Modal Form UI code goes here
        """
        return ui.row(
            ui.output_text(id="id_text"),ui.br(),
            ui.input_text(id="name",label=f"{self._title} Name *", value=self.__init_name()).add_style('color:red;'), #REQUIRED VALUE
        ),

    def server_call(self, input, output, session, summary_df):
        """
        Artist Modal Form Server code goes here
        """

        @module.server
        def input_form_func(input, output, session, summary_df):

            output_name = reactive.value('')
            
            @reactive.effect
            @reactive.event(input.btn_input_form_submit, ignore_init=True, ignore_none=True)
            def triggerInputFormSubmit():
                # Create single row as dataframe
                df_row_to_database = pd.DataFrame({'id':[self._df_selected_id],'name':[input.name()]})
                if self._df_selected_id:
                    self._db_table_model.update(df_row_to_database)
                else:
                    self._db_table_model.insert(df_row_to_database)
                
                ui.modal_remove()
                self.processData()
                summary_df.set(self.df_summary)

            @render.text
            def id_text():
                if self._df_selected_id:
                    return "id: "+str(self._df_selected_id)
                else:
                    return "id: [NEW RECORD]"
            
            @reactive.effect
            @reactive.event(input.btn_input_cancel)
            def triggerInputCancel():
                ui.modal_remove()

            return self.df_summary.copy

        return input_form_func(self._namespace_id, summary_df)

class SongInputTableModel(ShinyInputTableModel):    

    __db_artist_model=None
    __artist_lookup=None

    def __init__(self, namespace_id:str, title:str, db_table_model:database.DatabaseModel, db_artist_model:database.DatabaseModel):
        self._namespace_id=namespace_id
        self._title=title
        self._db_table_model=db_table_model
        self.__db_artist_model = db_artist_model

    def processData(self):
        # There is more complex logic required to process the Song dataframe because it has the artist lookup field to worry about
        df_raw_song = self._db_table_model.df_raw
        df_raw_artist = self.__db_artist_model.df_raw
        df_resolved_song = df_raw_song.merge(df_raw_artist, how='left', left_on='composer', right_on='id').drop(['composer','id_y'],axis=1).rename({'id_x':'id','name':'Composer'},axis=1)
        df_resolved_song = df_resolved_song.merge(df_raw_artist, how='left', left_on='arranger', right_on='id').drop(['arranger','id_y'],axis=1).rename({'id_x':'id','name':'Arranger'},axis=1)
        df_resolved_song['Start Date'] = pd.to_datetime(df_resolved_song['start_date']).dt.strftime("%m/%d/%Y")
        df_resolved_song['Off Book Date'] = pd.to_datetime(df_resolved_song['off_book_date']).dt.strftime("%m/%d/%Y")
        df_resolved_song['Play Ready Date'] = pd.to_datetime(df_resolved_song['play_ready_date']).dt.strftime("%m/%d/%Y")
        df_resolved_song = df_resolved_song.rename({'title':'Title'},axis=1)
        self.df_summary = df_resolved_song[['id','Title','Composer','Start Date','Off Book Date','Play Ready Date']]

        # Establish artist lookup
        self.__artist_lookup = {'':''}
        self.__artist_lookup.update({value:label for value,label in zip(df_raw_artist['id'],df_raw_artist['name'])})
        #self.__artist_lookup[None]=None

    def __init_title(self):
        # provide initial value for the name field of the input form
        if self._df_selected_id:
            return str(self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['title'].values[0])
        else:
            # User selected New
            return None
        
    def __init_composer(self):
        # provide initial value for the composer lookup field of the input form
        if self._df_selected_id:
            # User selected Update
            artist_id = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['composer'].values[0]
            if (artist_id):
                if (not math.isnan(artist_id)):
                    return int(artist_id) # Update a record with a non-null artist selection
                    '' # Update a record with a null artist id
            else:
                return '' # Update a record with a null artist id
        else:
            # User selected New
            return '' # New Record, there is no value     
  

    def __init_arranger(self):
        # provide initial value for the arranger lookup field of the input form
        if self._df_selected_id: 
            # User selected Update
            artist_id = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['arranger'].values[0]
            if (artist_id):
                if (not math.isnan(artist_id)):
                    return int(artist_id) # Update a record with a non-null artist selection
                    '' # Update a record with a null artist id
            else:
                return '' # Update a record with a null artist id
        else:
            # User selected New
            return '' # New Record, there is no value     

    def __init_start_date(self):
        # provide initial value for the start date on the input form
        if self._df_selected_id:
            # User selected Update
            start_date = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['start_date'].values[0]
            if start_date:
                return start_date
            else:
                return pd.NaT
            # User selected New
        else:
            return pd.NaT     
        
    def __init_off_book_date(self):
        # provide initial value for the off_book_date on the input form
        if self._df_selected_id:
            # User selected Update
            off_book_date = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['off_book_date'].values[0]
            if off_book_date:
                return off_book_date
            else:
                return pd.NaT
            # User selected New
        else:
            return pd.NaT     
        
    def __init_play_ready_date(self):
        # provide initial value for the play_ready_date on the input form
        if self._df_selected_id:
            # User selected Update
            play_ready_date = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['play_ready_date'].values[0]
            if play_ready_date:
                return play_ready_date
            else:
                return pd.NaT
            # User selected New
        else:
            return pd.NaT      
         
    def _ui_specific_code(self):
        """
        Song Modal Form UI code goes here
        """
        return ui.row(
            ui.output_text(id="id_text"),ui.br(),
            ui.input_text(id="title",label=f"{self._title} Title *", value=self.__init_title()).add_style('color:red;'), # REQUIRED VALUE
            ui.input_select(id="composer",label="Composer",choices=self.__artist_lookup, selected=self.__init_composer()),
            ui.input_select(id="arranger",label="Arranger",choices=self.__artist_lookup, selected=self.__init_arranger()),
            ui.input_date(id="start_date", label="Start Date",value=self.__init_start_date()),
            ui.input_date(id="off_book_date", label="Off Book Date",value=pd.NaT),
            ui.input_date(id="play_ready_date", label="Play Ready Date",value=pd.NaT),
        ),

    def server_call(self, input, output, session, summary_df):
        """
        Song Modal Form Server code goes here
        """

        @module.server
        def input_form_func(input, output, session, summary_df):

            output_name = reactive.value('')
            
            @reactive.effect
            @reactive.event(input.btn_input_form_submit, ignore_init=True, ignore_none=True)
            def triggerInputFormSubmit():
                composer_id = None if input.composer() == '' else input.composer()
                arranger_id = None if input.arranger() == '' else input.arranger()
                # Create single row as dataframe
                df_row_to_database = pd.DataFrame({'id':[self._df_selected_id],
                                                   'title':[input.title()], # REQUIRED VALUE
                                                   'composer':[composer_id],
                                                   'arranger':[arranger_id],
                                                   'start_date':[input.start_date()],
                                                   'off_book_date':[input.off_book_date()],
                                                   'play_ready_date':[input.play_ready_date()]})
                if self._df_selected_id:
                    self._db_table_model.update(df_row_to_database)
                else:
                    self._db_table_model.insert(df_row_to_database)
                
                ui.modal_remove()
                self.processData()
                summary_df.set(self.df_summary)

            @render.text
            def id_text():
                if self._df_selected_id:
                    return "id: "+str(self._df_selected_id)
                else:
                    return "id: [NEW RECORD]"
            
            @reactive.effect
            @reactive.event(input.btn_input_cancel)
            def triggerInputCancel():
                ui.modal_remove()

            return self.df_summary.copy

        return input_form_func(self._namespace_id, summary_df)


class SessionInputTableModel(ShinyInputTableModel):    

    __db_artist_model=None
    __db_song_model=None
    __song_lookup=None

    def __init__(self, namespace_id:str, title:str, db_table_model:database.DatabaseModel, db_song_model:database.DatabaseModel, db_artist_model:database.DatabaseModel):
        self._namespace_id=namespace_id
        self._title=title
        self._db_table_model=db_table_model
        self.__db_artist_model = db_artist_model
        self.__db_song_model = db_song_model
        
        
    def processData(self):
        # There is more complex logic required to process the Song dataframe because it has the artist lookup field to worry about
        
        df_raw_session = self._db_table_model.df_raw
        df_raw_song = self.__db_song_model.df_raw
        df_raw_artist = self.__db_artist_model.df_raw
        df_resolved_song = df_raw_song.merge(df_raw_artist, how='left', left_on='composer', right_on='id').drop(['composer','id_y'],axis=1).rename({'id_x':'id','name':'Composer'},axis=1)
        df_resolved_song = df_resolved_song.merge(df_raw_artist, how='left', left_on='arranger', right_on='id').drop(['arranger','id_y'],axis=1).rename({'id_x':'id','name':'Arranger'},axis=1)
        df_resolved_song['Start Date'] = pd.to_datetime(df_resolved_song['start_date']).dt.strftime("%m/%d/%Y")
        df_resolved_song['Off Book Date'] = pd.to_datetime(df_resolved_song['off_book_date']).dt.strftime("%m/%d/%Y")
        df_resolved_song['Play Ready Date'] = pd.to_datetime(df_resolved_song['play_ready_date']).dt.strftime("%m/%d/%Y")
        df_resolved_song = df_resolved_song.rename({'title':'Title'},axis=1)
        df_resolved_sessions = df_raw_session.merge(df_resolved_song,how='left', left_on='l_song_id', right_on='id').drop(['l_song_id','id_y'],axis=1).rename({'id_x':'id'},axis=1)
        df_resolved_sessions['Session Date'] = pd.to_datetime(df_resolved_sessions['session_date']).dt.strftime("%m/%d/%Y")
        df_resolved_sessions = df_resolved_sessions.rename({'duration':'Duration','notes':'Notes','Title':'Song','video_url':'Video URL'},axis=1)
        self.df_summary = df_resolved_sessions[['id', 'Session Date', 'Duration', 'Song','Composer','Notes', 'Video URL']].sort_values('Session Date', ascending=False)
        
        # Establish song lookup
        self.__song_lookup = {'':''}
        self.__song_lookup.update({value:label for value,label in zip(df_raw_song['id'],df_raw_song['title'])})

    def __init_session_date(self):
        # provide initial value for the start date on the input form
        if self._df_selected_id:
            # User selected Update
            session_date = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['session_date'].values[0]
            if session_date:
                return session_date
            else:
                return pd.NaT
            # User selected New
        else:
            return pd.NaT

    def __init_song(self):
        # provide initial value for the composer lookup field of the input form
        if self._df_selected_id:
            # User selected Update
            song_id = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['l_song_id'].values[0]
            if (song_id):
                if (not math.isnan(song_id)):
                    return int(song_id) # Update a record with a non-null artist selection
                    '' # Update a record with a null artist id
            else:
                return '' # Update a record with a null artist id
        else:
            # User selected New
            return '' # New Record, there is no value     
  
    def __init_duration(self):
        # provide initial value for the duration field of the input form
        if self._df_selected_id:
            return int(self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['duration'].values[0])
        else:
            # User selected New
            return None
        
    def __init_notes(self):
        # provide initial value for the duration field of the input form
        if self._df_selected_id:
            return self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['notes'].values[0]
        else:
            # User selected New
            return None        

    def __init_video_url(self):
        # provide initial value for the duration field of the input form
        if self._df_selected_id:
            return self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['video_url'].values[0]
        else:
            # User selected New
            return None 

    def _ui_specific_code(self):
        """
        Song Modal Form UI code goes here
        """
        return ui.row(
            ui.output_text(id="id_text"),ui.br(),
            ui.input_date(id="session_date",label=f"Session Date *", value=self.__init_session_date()).add_style('color:red;'), #REQUIRED FIELD
            ui.input_text(id="duration",label="Duration *", value=self.__init_duration()).add_style('color:red;'), #REQUIRED FIELD
            ui.input_select(id="song_id",label="Song",choices=self.__song_lookup, selected=self.__init_song()),
            ui.input_text_area(id="notes", label="Session Notes",value=self.__init_notes()),
            ui.input_text(id="video_url", label="Video Url (YouTube)",value=self.__init_video_url()),
        ),

    def server_call(self, input, output, session, summary_df):
        """
        Song Modal Form Server code goes here
        """

        @module.server
        def input_form_func(input, output, session, summary_df):

            output_name = reactive.value('')
            
            @reactive.effect
            @reactive.event(input.btn_input_form_submit, ignore_init=True, ignore_none=True)
            def triggerInputFormSubmit():
                with reactive.isolate():
                    print(f"Input button value [{input.btn_input_form_submit()}]")
                    print("Input Submit Pressed!")
                    song_id = None if input.song_id() == '' else input.song_id()
                    # Create single row as dataframe
                    df_row_to_database = pd.DataFrame({'id':[self._df_selected_id],
                                                    'session_date':[input.session_date()],
                                                    'duration':[input.duration()],
                                                    'l_song_id':[song_id],
                                                    'notes':[input.notes()]})
                    if self._df_selected_id:
                        self._db_table_model.update(df_row_to_database)
                    else:
                        self._db_table_model.insert(df_row_to_database)
                    
                    ui.modal_remove()
                    self.processData()
                    summary_df.set(self.df_summary)

            @render.text
            def id_text():
                if self._df_selected_id:
                    return "id: "+str(self._df_selected_id)
                else:
                    return "id: [NEW RECORD]"
           
            @reactive.effect
            @reactive.event(input.btn_input_cancel)
            def triggerInputCancel():
                ui.modal_remove()

            return self.df_summary.copy

        return input_form_func(self._namespace_id, summary_df)

