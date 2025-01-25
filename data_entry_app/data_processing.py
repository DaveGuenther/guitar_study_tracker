# Core
import datetime
import pandas as pd
import numpy as np
import math
from abc import ABC, abstractmethod
from shiny import ui, module, render, reactive, req

import database

def default_func():
    pass

class ShinyInputTableModel(ABC):
    """
    This class will make use of DatabaseTableModels to establish more complete table representation for user form input (including where necessary bringing in lookup tables to resolve lookup ids in the primary table).  It also contains specific UI components required for the inpurt form modal.
    """
    df_summary=None # used to store the summarized view (with appropriate lookups resolved) that is provided to the table navigator
    _namespace_id=None # used as prefix for the shiny module (e.g. 'artist','arrangement')
    _title=None # used for displaying in form titles in the shiny module (e.g. 'Artist','Arrangement')
    _db_table_model=None # This object manages read/write access to the specific table itself (database model)
    _df_selected_id = None # This is the selected row passed in from the table navigator
    _input_form_modal = None # This is the input form modal's id.  We use this to close the modal in the concrete class definitions
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
            self._input_form_modal = ui.modal(
                self._ui_specific_code(),
                ui.row(
                    ui.column(4, ui.input_action_button("btn_input_cancel","Cancel",width="100%")),
                    ui.column(4),
                    ui.column(4, ui.input_action_button("btn_input_form_submit", "Submit", width="100%", disabled=self._db_table_model.isReadOnly())),
                    ui.output_text(id='data_validation_text').add_style('color:red;'),
                ),
                title=f"Input Form - New {self._title}",
                easy_close=True,
                footer=None,
            )
            return ui.modal_show(self._input_form_modal)

        return ui_modal(self._namespace_id)

    def _init_id_text(self):
        if self._df_selected_id:
            return "id: "+str(self._df_selected_id)
        else:
            return "id: [NEW RECORD]"        

    @abstractmethod
    def server_call(self, input, output, session, summary_df):
        pass

class ArtistInputTableModel(ShinyInputTableModel):    

    def __init__(self, namespace_id:str, title:str, db_table_model:database.DatabaseModel):
        self._namespace_id=namespace_id
        self._title=title
        self._db_table_model=db_table_model

    def processData(self):
        self._db_table_model.df_raw['last_name']=self._db_table_model.df_raw['name'].str.split(' ').str[-1]
        self._db_table_model.df_raw = self._db_table_model.df_raw.sort_values('last_name')
        self.df_summary = self._db_table_model.df_raw.rename({'name':'Artist'},axis=1).copy()
        self.df_summary = self.df_summary[['id','Artist']]

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
            ui.div(self._init_id_text()),
            ui.input_text(id="name",label=f"{self._title} Name *", value=self.__init_name()).add_style('color:red;'), #REQUIRED VALUE
        ),

    def server_call(self, input, output, session, summary_df):
        """
        Artist Modal Form Server code goes here
        """

        @module.server
        def input_form_func(input, output, session, summary_df):

            output_name = reactive.value('')
            data_validation_msg = reactive.value('')
            
            @reactive.effect
            @reactive.event(input.btn_input_form_submit, ignore_init=True, ignore_none=True)
            def triggerInputFormSubmit():
                # Perform Data Validation and msg if issues
                try:
                    req(input.name())
                except:
                    data_validation_msg.set('Please fill in all required form fields!')
                    return
                else:
                    data_validation_msg.set('')

                # Create single row as dataframe
                df_row_to_database = pd.DataFrame({'id':[self._df_selected_id],'name':[input.name()]})
                if self._df_selected_id:
                    self._db_table_model.update(df_row_to_database)
                else:
                    self._db_table_model.insert(df_row_to_database)
                
                ui.modal_remove()
                self.processData()
                summary_df.set(self.df_summary)
           
            @reactive.effect
            @reactive.event(input.btn_input_cancel)
            def triggerInputCancel():
                ui.modal_remove()

            @render.text
            def data_validation_text():
                return data_validation_msg()

            return self.df_summary.copy

        return input_form_func(self._namespace_id, summary_df)


class StringSetInputTableModel(ShinyInputTableModel):    

    def __init__(self, namespace_id:str, title:str, db_table_model:database.DatabaseModel):
        self._namespace_id=namespace_id
        self._title=title
        self._db_table_model=db_table_model

    def processData(self):
        self._db_table_model.df_raw = self._db_table_model.df_raw.sort_values('name')
        self.df_summary = self._db_table_model.df_raw.rename({'name':'Name', 'hyperlink':'Hyperlink'},axis=1).copy()

    def __init_name(self):
        if self._df_selected_id:
            # provide initial value for the name field of the input form
            return str(self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['name'].values[0])
        else:
            return None

    def __init_hyperlink(self):
        if self._df_selected_id:
            # provide initial value for the hyperlink field of the input form
            return str(self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['hyperlink'].values[0])
        else:
            return None

    def __init_image_url(self):
        if self._df_selected_id:
            # provide initial value for the image field of the input form
            return str(self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['image_url'].values[0])
        else:
            return None        

    def _ui_specific_code(self):
        """
        String Set Modal Form UI code goes here
        """
        return ui.row(
            ui.div(self._init_id_text()),
            ui.input_text(id="name",label=f"{self._title} Name *", value=self.__init_name()).add_style('color:red;'), #REQUIRED VALUE
            ui.input_text(id="hyperlink",label=f"{self._title} Hyperlink", value=self.__init_hyperlink()),
            ui.input_text(id="image_url",label=f"{self._title} Image URL", value=self.__init_image_url()),
        ),

    def server_call(self, input, output, session, summary_df):
        """
        Artist Modal Form Server code goes here
        """

        @module.server
        def input_form_func(input, output, session, summary_df):

            output_name = reactive.value('')
            data_validation_msg = reactive.value('')

            @reactive.effect
            @reactive.event(input.btn_input_form_submit, ignore_init=True, ignore_none=True)
            def triggerInputFormSubmit():
                # Perform Data Validation and msg if issues
                try:
                    req(input.name())
                except:
                    data_validation_msg.set('Please fill in all required form fields!')
                    return
                else:
                    data_validation_msg.set('')

                # Data Validation Passed - Write database row

                # Create single row as dataframe
                df_row_to_database = pd.DataFrame({'id':[self._df_selected_id],
                                                   'name':[input.name()],
                                                   'hyperlink':[input.hyperlink()],
                                                   'image_url':[input.image_url()]})
                if self._df_selected_id:
                    self._db_table_model.update(df_row_to_database)
                else:
                    self._db_table_model.insert(df_row_to_database)
                
                ui.modal_remove()
                self.processData()
                summary_df.set(self.df_summary)
           
            @reactive.effect
            @reactive.event(input.btn_input_cancel)
            def triggerInputCancel():
                ui.modal_remove()

            @render.text
            def data_validation_text():
                return data_validation_msg()

            return self.df_summary.copy

        return input_form_func(self._namespace_id, summary_df)


class StyleInputTableModel(ShinyInputTableModel):    

    def __init__(self, namespace_id:str, title:str, db_table_model:database.DatabaseModel):
        self._namespace_id=namespace_id
        self._title=title
        self._db_table_model=db_table_model

    def processData(self):
        self._db_table_model.df_raw = self._db_table_model.df_raw.sort_values('style')
        self.df_summary = self._db_table_model.df_raw.rename({'style':'Style'},axis=1).copy()

    def __init_name(self):
        if self._df_selected_id:
            # provide initial value for the name field of the input form
            return str(self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['style'].values[0])
        else:
            return None
    
    def _ui_specific_code(self):
        """
        Artist Modal Form UI code goes here
        """
        return ui.row(
            ui.div(self._init_id_text()),
            ui.input_text(id="style",label=f"{self._title} Name *", value=self.__init_name()).add_style('color:red;'), #REQUIRED VALUE
        ),

    def server_call(self, input, output, session, summary_df):
        """
        Artist Modal Form Server code goes here
        """

        @module.server
        def input_form_func(input, output, session, summary_df):

            output_name = reactive.value('')
            data_validation_msg = reactive.value('')

            @reactive.effect
            @reactive.event(input.btn_input_form_submit, ignore_init=True, ignore_none=True)
            def triggerInputFormSubmit():
                # Perform Data Validation and msg if issues
                try:
                    req(input.style())
                except:
                    data_validation_msg.set('Please fill in all required form fields!')
                    return
                else:
                    data_validation_msg.set('')

                # Data Validation Passed - Write database row

                # Create single row as dataframe
                df_row_to_database = pd.DataFrame({'id':[self._df_selected_id],'style':[input.style()]})
                if self._df_selected_id:
                    self._db_table_model.update(df_row_to_database)
                else:
                    self._db_table_model.insert(df_row_to_database)
                
                ui.modal_remove()
                self.processData()
                summary_df.set(self.df_summary)
           
            @reactive.effect
            @reactive.event(input.btn_input_cancel)
            def triggerInputCancel():
                ui.modal_remove()

            @render.text
            def data_validation_text():
                return data_validation_msg()

            return self.df_summary.copy

        return input_form_func(self._namespace_id, summary_df)

class SongInputTableModel(ShinyInputTableModel):    

    __db_artist_model=None
    __artist_lookup=None
    __style_lookup=None
    __song_type_lookup={'Song':'Song','Exercise':'Exercise'} # Too lazy to make a lookup table for two values.  I'll do it is there's ever a third type

    def __init__(self, namespace_id:str, title:str, db_table_model:database.DatabaseModel, db_artist_model:database.DatabaseModel, db_style_model:database.DatabaseModel):
        self._namespace_id=namespace_id
        self._title=title
        self._db_table_model=db_table_model
        self.__db_artist_model = db_artist_model
        self.__db_style_model = db_style_model

    def processData(self):
        # There is more complex logic required to process the Song dataframe because it has the artist lookup field to worry about
        df_raw_song = self._db_table_model.df_raw
        df_raw_artist = self.__db_artist_model.df_raw
        df_raw_style = self.__db_style_model.df_raw
        df_raw_song['style_id'] = df_raw_song['style_id'].astype("Int64") # Allows us to join on null ints since this column is nullable
        df_raw_song['composer_id'] = df_raw_song['composer_id'].astype("Int64") # Allows us to join on null ints since this column is nullable
        df_resolved_song = df_raw_song.merge(df_raw_artist, how='left', left_on='composer_id', right_on='id').drop(['composer_id','id_y'],axis=1).rename({'id_x':'id','name':'Composer'},axis=1)
        df_resolved_song = df_resolved_song.merge(df_raw_style, how='left', left_on='style_id', right_on='id').drop(['style_id','id_y'], axis=1).rename({'id_x':'id', 'style':'Style'},axis=1)
        df_resolved_song = df_resolved_song.rename({'title':'Title', 'song_type':'Song Type'},axis=1).sort_values(['last_name','Title'])
        self.df_summary = df_resolved_song[['id','Title','Composer','Song Type','Style']]


        # Establish artist lookup
        self.__artist_lookup = {'':''}
        self.__artist_lookup.update({value:label for value,label in zip(df_raw_artist['id'],df_raw_artist['name'])})
        
        # Establish style lookup
        self.__style_lookup = {'':''}
        self.__style_lookup.update({value:label for value,label in zip(df_raw_style['id'],df_raw_style['style'])})

        

        

    def __init_title(self):
        # provide initial value for the title field of the input form
        if self._df_selected_id:
            return str(self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['title'].values[0])
        else:
            # User selected New
            return None

    def __init_song_type(self):
        # provide initial value for the song_type field of the input form
        if self._df_selected_id:
            return str(self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['song_type'].values[0])
        else:
            # User selected New
            return None
        

    def __init_composer(self):
        # provide initial value for the composer lookup field of the input form
        if self._df_selected_id: 
            # User selected Update
            artist_id = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['composer_id'].values[0]
            if pd.isna(artist_id):
                return '' # Update a record with a null artist id

            else:
                if (not math.isnan(artist_id)):
                    return int(artist_id) # Update a record with a non-null artist selection
                '' # Update a record with a null artist id
        else:
            # User selected New
            return '' # New Record, there is no value   
  

    def __init_style(self):
        # provide initial value for the style lookup field of the input form
        if self._df_selected_id: 
            # User selected Update
            style_id = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['style_id'].values[0]
            if pd.isna(style_id):
                return '' # Update a record with a null artist id

            else:
                if (not math.isnan(style_id)):
                    return int(style_id) # Update a record with a non-null artist selection
                '' # Update a record with a null artist id
        else:
            # User selected New
            return '' # New Record, there is no value    
         
    def _ui_specific_code(self):
        """
        Song Modal Form UI code goes here
        """
        return ui.row(
            ui.div(self._init_id_text()),
            ui.input_text(id="title",label=f"{self._title} Title *", value=self.__init_title()).add_style('color:red;'), # REQUIRED VALUE
            ui.input_select(id='song_type', label="Song Type", choices=self.__song_type_lookup, selected=self.__init_song_type()),
            ui.input_select(id='style',label="Style", choices=self.__style_lookup, selected=self.__init_style()),
            ui.input_select(id="composer",label="Composer",choices=self.__artist_lookup, selected=self.__init_composer()),
        ),

    def server_call(self, input, output, session, summary_df):
        """
        Song Modal Form Server code goes here
        """

        @module.server
        def input_form_func(input, output, session, summary_df):

            output_name = reactive.value('')
            data_validation_msg = reactive.value('')

            @reactive.effect
            @reactive.event(input.btn_input_form_submit, ignore_init=True, ignore_none=True)
            def triggerInputFormSubmit():
                # Perform Data Validation and msg if issues
                try:
                    req(input.title())
                except:
                    data_validation_msg.set('Please fill in all required form fields!')
                    return
                else:
                    data_validation_msg.set('')

                # Data Validation Passed - Write database row

                composer_id = None if input.composer() == '' else input.composer()
                style_id = None if input.style() == '' else input.style()
                song_type = None if input.song_type() == '' else input.song_type()
                # Create single row as dataframe
                df_row_to_database = pd.DataFrame({'id':[self._df_selected_id],
                                                   'title':[input.title()], # REQUIRED VALUE
                                                   'style_id':[style_id],
                                                   'composer_id':[composer_id],
                                                   'song_type':[song_type]})

                if self._df_selected_id:
                    self._db_table_model.update(df_row_to_database)
                else:
                    self._db_table_model.insert(df_row_to_database)
                
                ui.modal_remove()
                self.processData()
                summary_df.set(self.df_summary)
            
            @reactive.effect
            @reactive.event(input.btn_input_cancel)
            def triggerInputCancel():
                ui.modal_remove()

            @render.text
            def data_validation_text():
                return data_validation_msg()
            
            return self.df_summary.copy

        return input_form_func(self._namespace_id, summary_df)


class ArrangementInputTableModel(ShinyInputTableModel):    

    __db_artist_model=None
    __artist_lookup=None
    __difficulty_lookup=None
    __song_lookup=None

    def __init__(self, namespace_id:str, title:str, db_table_model:database.DatabaseModel, db_song_model:database.DatabaseModel, db_artist_model:database.DatabaseModel, db_style_model:database.DatabaseModel):
        self._namespace_id=namespace_id
        self._title=title
        self._db_table_model=db_table_model
        self.__db_artist_model = db_artist_model
        self.__db_style_model = db_style_model
        self.__db_song_model = db_song_model 

    def processData(self):
        # There is more complex logic required to process the Arrangement dataframe because it has the artist lookup field to worry about
        df_raw_arrangement = self._db_table_model.df_raw
        df_raw_artist = self.__db_artist_model.df_raw
        df_raw_style = self.__db_style_model.df_raw
        df_raw_song = self.__db_song_model.df_raw
        df_resolved_song = df_raw_song.merge(df_raw_artist, how='left', left_on='composer_id', right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id','name':'composer'},axis=1)
        df_resolved_song = df_resolved_song.merge(df_raw_style, how='left', left_on='style_id', right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id'},axis=1)

        df_raw_arrangement['arranger'] = df_raw_arrangement['arranger'].astype("Int64") # Allows us to join on null ints since this column is nullable
        df_resolved_arrangement = df_raw_arrangement.merge(df_raw_artist, how='left', left_on='arranger', right_on='id').drop(['arranger','id_y','last_name'],axis=1).rename({'id_x':'id','name':'Arranger'},axis=1)
        df_resolved_arrangement = df_resolved_arrangement.merge(df_resolved_song, how='left',left_on='song_id',right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id'},axis=1)

        df_resolved_arrangement['Start Date'] = pd.to_datetime(df_resolved_arrangement['start_date']).dt.strftime("%m/%d/%Y")
        df_resolved_arrangement['At Tempo Date'] = pd.to_datetime(df_resolved_arrangement['at_tempo_date']).dt.strftime("%m/%d/%Y")
        df_resolved_arrangement['Off Book Date'] = pd.to_datetime(df_resolved_arrangement['off_book_date']).dt.strftime("%m/%d/%Y")
        df_resolved_arrangement['Play Ready Date'] = pd.to_datetime(df_resolved_arrangement['play_ready_date']).dt.strftime("%m/%d/%Y")
        df_resolved_arrangement = df_resolved_arrangement.rename({'title':'Title', 'composer':'Composer','song_type':'Song Type','difficulty':'Difficulty','sheet_music_link':'Sheet Music Link','performance_link':'Performance Link','style':'Style'},axis=1).sort_values(['last_name','Title'])
        self.df_summary = df_resolved_arrangement[['id','Title','Composer','Song Type','Style','Start Date','Off Book Date','At Tempo Date','Play Ready Date','Difficulty','Sheet Music Link','Performance Link']]


        # Establish artist lookup
        self.__artist_lookup = {'':''}
        self.__artist_lookup.update({value:label for value,label in zip(df_raw_artist['id'],df_raw_artist['name'])})

        # Establish song lookup
        self.__song_lookup = {'':''}
        self.__song_lookup.update({value:label for value,label in zip(df_raw_song['id'],df_raw_song['title'])})

        
        # Establish difficulty lookup
        self.__difficulty_lookup = {'':''}
        self.__difficulty_lookup.update({'Beginner':'Beginner','Intermediate':'Intermediate','Advanced':'Advanced'})



    def __init_difficulty(self):
        # provide initial value for the name field of the input form
        if self._df_selected_id:
            return str(self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['difficulty'].values[0])
        else:
            # User selected New
            return None

    def __init_sheet_music_link(self):
        # provide initial value for the name field of the input form
        if self._df_selected_id:
            return str(self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['sheet_music_link'].values[0])
        else:
            # User selected New
            return None

    def __init_performance_link(self):
        # provide initial value for the name field of the input form
        if self._df_selected_id:
            return str(self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['performance_link'].values[0])
        else:
            # User selected New
            return None

    def __init_arranger(self):
        # provide initial value for the arranger lookup field of the input form
        if self._df_selected_id: 
            # User selected Update
            artist_id = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['arranger'].values[0]
            if pd.isna(artist_id):
                return '' # Update a record with a null artist id

            else:
                if (not math.isnan(artist_id)):
                    return int(artist_id) # Update a record with a non-null artist selection
                '' # Update a record with a null artist id
        else:
            # User selected New
            return '' # New Record, there is no value    


    def __init_song(self):
        # provide initial value for the arranger lookup field of the input form
        if self._df_selected_id: 
            # User selected Update
            song_id = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['song_id'].values[0]
            if pd.isna(song_id):
                return '' # Update a record with a null artist id

            else:
                if (not math.isnan(song_id)):
                    return int(song_id) # Update a record with a non-null artist selection
                '' # Update a record with a null artist id
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
        
    def __init_at_tempo_date(self):
        # provide initial value for the off_book_date on the input form
        if self._df_selected_id:
            # User selected Update
            at_tempo_date = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['at_tempo_date'].values[0]
            if at_tempo_date:
                return at_tempo_date
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
        Arrangement Modal Form UI code goes here
        """
        return ui.row(
            ui.div(self._init_id_text()),
            ui.input_select(id='song', label="Song", choices=self.__song_lookup, selected=self.__init_song()),
            ui.input_select(id="arranger",label="Arranger",choices=self.__artist_lookup, selected=self.__init_arranger()),
            ui.input_date(id="start_date", label="Start Date",value=self.__init_start_date()),
            ui.input_date(id="off_book_date", label="Off Book Date",value=self.__init_off_book_date()),
            ui.input_date(id="at_tempo_date", label="At Tempo Date",value=self.__init_at_tempo_date()),            
            ui.input_date(id="play_ready_date", label="Play Ready Date",value=self.__init_play_ready_date()),
            ui.input_text(id='difficulty', label='Difficulty', value = self.__init_difficulty()),
            ui.input_text(id='sheet_music_link', label='Sheet Music Link', value = self.__init_sheet_music_link()),
            ui.input_text(id='performance_link', label='Performance Link', value = self.__init_performance_link()),
        ),

    def server_call(self, input, output, session, summary_df):
        """
        Arrangement Modal Form Server code goes here
        """

        @module.server
        def input_form_func(input, output, session, summary_df):

            output_name = reactive.value('')
            data_validation_msg = reactive.value('')

            @reactive.effect
            @reactive.event(input.btn_input_form_submit, ignore_init=True, ignore_none=True)
            def triggerInputFormSubmit():
                # Perform Data Validation and msg if issues
                try:
                    req(input.song())
                except:
                    data_validation_msg.set('Please fill in all required form fields!')
                    return
                else:
                    data_validation_msg.set('')

                # Data Validation Passed - Write database row

                #print("Inside Submit")
                arranger_id = None if input.arranger() == '' else input.arranger()
                #style_id = None if input.style() == '' else input.style()
                song_id = None if input.song()=='' else input.song()
                # Create single row as dataframe
                df_row_to_database = pd.DataFrame({'id':[self._df_selected_id],
                                                   #'title':[input.title()], # REQUIRED VALUE
                                                   'song_id':[song_id], #REQUIRED
                                                   #'style_id':[style_id],
                                                   'difficulty':[input.difficulty()],
                                                   'sheet_music_link':[input.sheet_music_link()],
                                                   'performance_link':[input.performance_link()],
                                                   #'composer':[composer_id],
                                                   'arranger':[arranger_id],
                                                   'start_date':[input.start_date()],
                                                   'off_book_date':[input.off_book_date()],
                                                   'at_tempo_date':[input.at_tempo_date()],
                                                   'play_ready_date':[input.play_ready_date()]})
                #print(df_row_to_database.to_string())
                if self._df_selected_id:
                    self._db_table_model.update(df_row_to_database)
                else:
                    self._db_table_model.insert(df_row_to_database)
                
                ui.modal_remove()
                self.processData()
                summary_df.set(self.df_summary)
            
            @reactive.effect
            @reactive.event(input.btn_input_cancel)
            def triggerInputCancel():
                #print("Cancelled")
                ui.modal_remove()

            @render.text
            def data_validation_text():
                return data_validation_msg()
            
            return self.df_summary.copy

        return input_form_func(self._namespace_id, summary_df)


class ArrangementGoalInputTableModel(ShinyInputTableModel):    

    __db_arrangement_model=None
    __db_artist_model=None
    __db_song_model=None

    # We want the lookup control for arrangements on the form to show all arrangements on the arrangements table that aren't already on the goal arrangements table.
    # However, when we update an existing goal arrangement record, we also want to add that arrangement id to the arrangement lookup table for that instance of the modal so that is isn't blank when we click Update on the record.
    __arrangement_lookup={}  # Gets populated during _ui_specific_code() so that it can have dynamic values for Update records

    def __init__(self, namespace_id:str, title:str, db_table_model:database.DatabaseModel, db_arrangement_model:database.DatabaseModel, db_song_model:database.DatabaseModel, db_artist_model:database.DatabaseModel):
        self._namespace_id=namespace_id
        self._title=title
        self._db_table_model=db_table_model
        self.__db_arrangement_model = db_arrangement_model
        self.__db_artist_model = db_artist_model
        self.__db_song_model = db_song_model

    def processData(self):
        # There is more complex logic required to process the Arrangement dataframe because it has the artist lookup field to worry about
        df_raw_arrangement_goal = self._db_table_model.df_raw
        df_raw_artist = self.__db_artist_model.df_raw
        df_raw_arrangement = self.__db_arrangement_model.df_raw
        df_raw_song = self.__db_song_model.df_raw
        df_resolved_song = df_raw_song.merge(df_raw_artist, how='left', left_on='composer_id', right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id','name':'Composer'},axis=1)
        df_resolved_arrangement = df_raw_arrangement.merge(df_resolved_song,how='left',left_on='song_id',right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id'},axis=1)
        # Update this model to merge in song data

        df_resolved_arrangement['arranger'] = df_resolved_arrangement['arranger'].astype("Int64") # Allows us to join on null ints since this column is nullable
        df_resolved_arrangement = df_resolved_arrangement.merge(df_raw_artist, how='left', left_on='arranger', right_on='id').drop(['arranger','id_y'],axis=1).rename({'id_x':'id','name':'Arranger','last_name_x':'c_last_name','last_name_y':'a_last_name'},axis=1)
        
        
        df_resolved_arrangement_goal = df_raw_arrangement_goal.merge(df_resolved_arrangement, how='left', left_on='arrangement_id', right_on='id').drop(['id_y'], axis=1).rename({'id_x':'id'}, axis=1)
        df_resolved_arrangement['Start Date'] = pd.to_datetime(df_resolved_arrangement['start_date']).dt.strftime("%m/%d/%Y")
        self.__df_resolved_arrangement=df_resolved_arrangement.copy()


        # Build rendered dataframe for the table navigator
        df_summary = df_resolved_arrangement_goal.rename({'title':'Title', 'song_type':'Song Type','description':'Description','discovery_date':'Date Discovered'},axis=1).sort_values(['Date Discovered'], ascending=False)
        df_summary['Date Discovered'] = pd.to_datetime(df_summary['Date Discovered']).dt.strftime("%m/%d/%Y")
        self.df_summary = df_summary[['id','Title','Composer','Arranger','Date Discovered','Description']]


        # Establish arrangement lookup for the arrangement goals table
        arrangement_ids_on_goals_table = df_resolved_arrangement_goal['arrangement_id']
        df_arrangement_lookup = df_resolved_arrangement[~df_resolved_arrangement['id'].isin(arrangement_ids_on_goals_table)] # Arrangements from the arrangement table can only be added once to the goal table
        self.__new_arrangement_lookup = {'':''}
        self.__new_arrangement_lookup.update({value:str("Composer: "+str(composer)+", Arrangement: "+str(title)+', Arranger: '+str(arranger)) for value,composer,arranger,title in zip(df_arrangement_lookup['id'],df_arrangement_lookup['Composer'],df_arrangement_lookup['Arranger'],df_arrangement_lookup['title'])})   


        

    def __init_description(self):
        # provide initial value for the description field of the input form
        if self._df_selected_id:
            return str(self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['description'].values[0])
        else:
            # User selected New
            return None     

    def __init_arrangement(self):
        # provide initial value for the arrangement lookup field of the input form
        if self._df_selected_id: 
            # User selected Update
            arrangement_id = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['arrangement_id'].values[0]
            if pd.isna(arrangement_id):
                return '' # Update a record with a null arrangement id

            else:
                if (not math.isnan(arrangement_id)):
                    return int(arrangement_id) # Update a record with a non-null arrangement selection
                '' # Update a record with a null arrangement id
        else:
            # User selected New
            return '' # New Record, there is no value   
  
       
    def __init_discovery_date(self):
        # provide initial value for the discovery_date on the input form
        if self._df_selected_id:
            # User selected Update
            discovery_date = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['discovery_date'].values[0]
            if discovery_date:
                return discovery_date
            else:
                return pd.NaT
            # User selected New
        else:
            return pd.NaT      
         
    def _ui_specific_code(self):
        """
        Arrangement Goal Modal Form UI code goes here.
        """
        ###  This function is called from the Parent Abstract Class ShinyInputTableModel.  In order to addess private members from this child class, instead of using self.__value, we have to 
        ###  deliberately access the child's provate data from the parent class: self._ArrangementGoalInputTableModel__value.  I'm not exactly sure why, but python isn't able to resolve self.__value
        ###  in this function when it is called from the parent class.
        df_resolved_arrangement = self._ArrangementGoalInputTableModel__df_resolved_arrangement # pseudonym for self.__df_resolved_arrangement.
        self._ArrangementGoalInputTableModel__arrangement_lookup=self._ArrangementGoalInputTableModel__new_arrangement_lookup # pesudonym for self.__new_arrangement_lookup.  Lookup arrangement control contains only arrangements that aren't on the gosl arrangement table.
        if self._df_selected_id:
            # Add a record to the lookup arrangement control for the selected arrangement_id so that it shows when a form is updated
            arrangement_id = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['arrangement_id'].values[0]
            composer=df_resolved_arrangement[df_resolved_arrangement['id']==arrangement_id]['Composer'].values[0]
            arranger=df_resolved_arrangement[df_resolved_arrangement['id']==arrangement_id]['Arranger'].values[0]
            title=df_resolved_arrangement[df_resolved_arrangement['id']==arrangement_id]['title'].values[0]
            self._ArrangementGoalInputTableModel__arrangement_lookup.update({int(arrangement_id):str("Composer: "+str(composer)+", Arrangement: "+str(title)+', Arranger: '+str(arranger))})
            

        return ui.row(
            ui.div(self._init_id_text()),
            ui.input_select(id='arrangement_id', label="Select a Arrangement *", choices=self.__arrangement_lookup, selected=self.__init_arrangement()).add_style('color:red;'), # REQUIRED VALUE
            ui.input_text(id="description",label="Arrangement Description/Inspiration", value=self.__init_description()), 
            ui.input_date(id="discovery_date", label="Date Discovered",value=self.__init_discovery_date()).add_style('color:red;'), # REQUIRED VALUE
        ),

    def server_call(self, input, output, session, summary_df):
        """
        Arrangement Goal Modal Form Server code goes here
        """

        @module.server
        def input_form_func(input, output, session, summary_df):

            output_name = reactive.value('')
            data_validation_msg = reactive.value('')
            
            @reactive.effect
            @reactive.event(input.btn_input_form_submit, ignore_init=True, ignore_none=True)
            def triggerInputFormSubmit():
                # Perform Data Validation and msg if issues
                try:
                    req(input.discovery_date())
                    req(input.arrangement_id())

                except:
                    data_validation_msg.set('Please fill in all required form fields!')
                    return
                else:
                    data_validation_msg.set('')

                # Data Validation Passed - Write database row

                #print("Inside Submit")
                arrangement_id = None if input.arrangement_id() == '' else input.arrangement_id()
                # Create single row as dataframe
                df_row_to_database = pd.DataFrame({'id':[self._df_selected_id],
                                                   'arrangement_id':[arrangement_id], # REQUIRED VALUE
                                                   'description':[input.description()],
                                                   'discovery_date':[input.discovery_date()]})
                #print(df_row_to_database.to_string())
                if self._df_selected_id:
                    self._db_table_model.update(df_row_to_database)
                else:
                    self._db_table_model.insert(df_row_to_database)
                
                ui.modal_remove()
                self.processData()
                summary_df.set(self.df_summary)
            
            @reactive.effect
            @reactive.event(input.btn_input_cancel)
            def triggerInputCancel():
                #print("Cancelled")
                ui.modal_remove()

            @render.text
            def data_validation_text():
                return data_validation_msg()
            
            return self.df_summary.copy

        return input_form_func(self._namespace_id, summary_df)

class GuitarInputTableModel(ShinyInputTableModel):    

    __string_set_lookup=None
    __guitar_status_lookup={'Permanent':'Permanent','Temporary':'Temporary', 'Retired':'Retired'}

    def __init__(self, namespace_id:str, title:str, db_table_model:database.DatabaseModel, db_string_set_model:database.DatabaseModel):
        self._namespace_id=namespace_id
        self._title=title
        self._db_table_model=db_table_model
        self.__db_string_set_model = db_string_set_model
        self.__df_current_default_guitar=pd.DataFrame()
        
    def processData(self):
        # There is more complex logic required to process the Arrangement dataframe because it has the artist lookup field to worry about
        
        df_raw_guitar = self._db_table_model.df_raw
        df_raw_string_set = self.__db_string_set_model.df_raw
        self.__df_current_default_guitar = df_raw_guitar[df_raw_guitar['default_guitar']==True] # Retrieve current default guitar that shows up in the session modal in case we change the default to another guitar

        df_resolved_guitar = df_raw_guitar.merge(df_raw_string_set, how='left', left_on='string_set_id', right_on='id').drop(['id_y'], axis=1).rename({'id_x':'id'}, axis=1)
        df_resolved_guitar['default_msg'] = np.where(df_resolved_guitar['default_guitar'],'Default for new Sessions','')
        df_resolved_guitar = df_resolved_guitar.rename({'make':'Make','model':'Model','status':'Status','about':'About','date_added':'Date Added','date_retired':'Date Retired','name':'Strings', 'default_msg':'Default Guitar'},axis=1)
        df_resolved_guitar['Date Added'] = pd.to_datetime(df_resolved_guitar['Date Added']).dt.strftime("%m/%d/%Y")
        df_resolved_guitar['Date Retired'] = pd.to_datetime(df_resolved_guitar['Date Retired']).dt.strftime("%m/%d/%Y")
        self.df_summary = df_resolved_guitar[['id', 'Make', 'Model', 'Status', 'About', 'image_link', 'Date Added', 'Date Retired', 'Strings', 'Default Guitar']]
        
        # Establish strings lookup
        self.__string_set_lookup = {'':''}
        self.__string_set_lookup.update({value:f"{string_set}" for value,string_set in zip(df_raw_string_set['id'],df_raw_string_set['name'])})

    def __init_make(self):
        # provide initial value for the make field of the input form
        if self._df_selected_id:
            return self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['make'].values[0]
        else:
            # User selected New
            return None    

    def __init_default_guitar(self):
        if self._df_selected_id:
            return self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['default_guitar'].values[0]
        else:
            # User selected New
            return None        

    def __init_model(self):
        # provide initial value for the make field of the input form
        if self._df_selected_id:
            return self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['model'].values[0]
        else:
            # User selected New
            return None    

    def __init_about(self):
        # provide initial value for the make field of the input form
        if self._df_selected_id:
            return self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['about'].values[0]
        else:
            # User selected New
            return None

    def __init_status(self):
        if self._df_selected_id:
            return self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['status'].values[0]
        else:
            # User selected New
            return None

    def __init_image_link(self):
        # provide initial value for the make field of the input form
        if self._df_selected_id:
            return self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['image_link'].values[0]
        else:
            # User selected New
            return None

    def __init_date_added(self):
        # provide initial value for the start date on the input form
        if self._df_selected_id:
            # User selected Update
            date_started = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['date_added'].values[0]
            if date_started:
                return date_started
            else:
                return pd.NaT
            # User selected New
        else:
            return pd.NaT
        
    def __init_string_install_date(self):
        # provide initial value for the start date on the input form
        if self._df_selected_id:
            # User selected Update
            date_strings_installed = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['strings_install_date'].values[0]
            if date_strings_installed:
                return date_strings_installed
            else:
                return pd.NaT
            # User selected New
        else:
            return pd.NaT        

    def __init_date_retired(self):
        # provide initial value for the start date on the input form
        if self._df_selected_id:
            # User selected Update
            date_retired = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['date_retired'].values[0]
            if date_retired:
                return date_retired
            else:
                return pd.NaT
            # User selected New
        else:
            return pd.NaT

    def __init_string_set(self):
        # provide initial value for the string_set lookup field of the input form
        if self._df_selected_id:
            # User selected Update
            string_set_id = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['string_set_id'].values[0]
            if (string_set_id):
                if (not math.isnan(string_set_id)):
                    return int(string_set_id) # Update a record with a non-null selection
                    '' # Update a record with a null id
            else:
                return '' # Update a record with a null id
        else:
            # User selected New
            return '' # New Record, there is no value     
  
    def _ui_specific_code(self):
        """
        Guitar Modal Form UI code goes here
        """
        return ui.row(
            ui.div(self._init_id_text()),
            ui.input_text(id="make",label="Make *", value=self.__init_make()).add_style('color:red;'), #REQUIRED FIELD
            ui.input_text(id="model",label="Model *", value=self.__init_model()).add_style('color:red;'), #REQUIRED FIELD
            ui.input_select(id='status', label="Status *", choices=self.__guitar_status_lookup, selected=self.__init_status()).add_style('color:red;'), #REQUIRED FIELD
            ui.input_switch(id='default_guitar',label='Default Guitar', value=self.__init_default_guitar()),
            ui.input_text(id="about",label="About *", value=self.__init_about()).add_style('color:red;'), #REQUIRED FIELD,
            ui.input_text(id="image_link",label="Image Link", value=self.__init_image_link()),
            ui.input_date(id="date_added",label=f"Date Added", value=self.__init_date_added()),
            ui.input_date(id='date_strings_installed', label=f"Date Strings Installed", value=self.__init_string_install_date()),
            ui.input_date(id="date_retired",label=f"Date Retired", value=self.__init_date_retired()),
            ui.input_select(id="string_set_id",label="String Set *",choices=self.__string_set_lookup, selected=self.__init_string_set()).add_style('color:red;'), #REQUIRED FIELD
        ),

    def server_call(self, input, output, session, summary_df):
        """
        Arrangement Modal Form Server code goes here
        """

        @module.server
        def input_form_func(input, output, session, summary_df):

            output_name = reactive.value('')
            data_validation_msg = reactive.value('')
            
            @reactive.effect
            @reactive.event(input.btn_input_form_submit, ignore_init=True, ignore_none=True)
            def triggerInputFormSubmit():
                # Data validation and message
                try:
                    req(input.make())
                    req(input.model())
                    req(input.status())
                    req(input.about())
                    req(input.string_set_id())
                except:
                    data_validation_msg.set('Please fill in all required form fields!')
                    return
                else:
                    data_validation_msg.set('')

                # Data Validation Passed - Write database row
                string_set_id = None if input.string_set_id() == '' else input.string_set_id()
                # Create single row as dataframe
                df_row_to_database = pd.DataFrame({'id':[self._df_selected_id],
                                                'make':[input.make()],
                                                'model':[input.model()],
                                                'status':[input.status()],
                                                'default_guitar':[input.default_guitar()],
                                                'about':[input.about()],
                                                'image_link':[input.image_link()],
                                                'date_added':[input.date_added()],
                                                'strings_install_date':[input.date_strings_installed()],
                                                'date_retired':[input.date_retired()],
                                                'string_set_id':[string_set_id]})
                
                # Any other guitars that are identified as default that aren't this one must be changed to default_guitar=False
                if input.default_guitar()==True:
                    for i in self._GuitarInputTableModel__df_current_default_guitar.index:
                        ser_previous_default_guitar = pd.Series(self._GuitarInputTableModel__df_current_default_guitar.loc[i])
                        if (not self._df_selected_id):
                            # Remove "default"guitar flag for previous guitars because this is a NEW record and is default
                            ser_previous_default_guitar['default_guitar']=False
                            df_previous_default_guitar = pd.DataFrame([ser_previous_default_guitar.copy()])
                            df_previous_default_guitar['string_set_id'] = df_previous_default_guitar['string_set_id'].astype(object)
                            self._db_table_model.update(df_previous_default_guitar)   
                        
                        elif (int(self._df_selected_id)!=int(ser_previous_default_guitar['id'])): # don't do anything if the default guitar hasn't changed and this is an update record
                            
                            ser_previous_default_guitar['default_guitar']=False
                            df_previous_default_guitar = pd.DataFrame([ser_previous_default_guitar.copy()])
                            df_previous_default_guitar['string_set_id'] = df_previous_default_guitar['string_set_id'].astype(object)
                            self._db_table_model.update(df_previous_default_guitar)       

                if self._df_selected_id:
                    self._db_table_model.update(df_row_to_database)
                    pass
                else:
                    self._db_table_model.insert(df_row_to_database)
                
                ui.modal_remove()
                self.processData()
                summary_df.set(self.df_summary)
           
            @reactive.effect
            @reactive.event(input.btn_input_cancel)
            def triggerInputCancel():
                ui.modal_remove()

            @render.text
            def data_validation_text():
                return data_validation_msg()

            return self.df_summary.copy
        


        return input_form_func(self._namespace_id, summary_df)



class SessionInputTableModel(ShinyInputTableModel):    

    __db_artist_model=None
    __db_arrangement_model=None
    __db_song_model=None
    __arrangement_lookup=None
    __guitar_lookup=None

    def __init__(self, namespace_id:str, title:str, db_table_model:database.DatabaseModel, db_arrangement_model:database.DatabaseModel, db_song_model:database.DatabaseModel, db_artist_model:database.DatabaseModel, db_guitar_model:database.DatabaseModel):
        self._namespace_id=namespace_id
        self._title=title
        self._db_table_model=db_table_model
        self.__db_artist_model = db_artist_model
        self.__db_arrangement_model = db_arrangement_model
        self.__db_guitar_model = db_guitar_model
        self.__db_song_model = db_song_model
        
        
    def processData(self):
        # There is more complex logic required to process the Arrangement dataframe because it has the artist lookup field to worry about
        
        df_raw_session = self._db_table_model.df_raw
        df_raw_arrangement = self.__db_arrangement_model.df_raw
        df_raw_artist = self.__db_artist_model.df_raw
        df_raw_guitar = self.__db_guitar_model.df_raw
        df_raw_song = self.__db_song_model.df_raw
        df_resolved_song = df_raw_song.merge(df_raw_artist, how='left', left_on='composer_id', right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id','name':'Composer'},axis=1)
        df_raw_arrangement['arranger'] = df_raw_arrangement['arranger'].astype("Int64") # Allows us to join on null ints since this column is nullable
        
        df_resolved_arrangement = df_raw_arrangement.merge(df_resolved_song, how='left', left_on='song_id', right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id'},axis=1)
        
        df_resolved_arrangement = df_resolved_arrangement.merge(df_raw_artist, how='left', left_on='arranger', right_on='id').drop(['arranger','id_y'],axis=1).rename({'id_x':'id','name':'Arranger'},axis=1)
        df_resolved_arrangement['Start Date'] = pd.to_datetime(df_resolved_arrangement['start_date']).dt.strftime("%m/%d/%Y")
        df_resolved_arrangement['Off Book Date'] = pd.to_datetime(df_resolved_arrangement['off_book_date']).dt.strftime("%m/%d/%Y")
        df_resolved_arrangement['Play Ready Date'] = pd.to_datetime(df_resolved_arrangement['play_ready_date']).dt.strftime("%m/%d/%Y")
        df_resolved_arrangement = df_resolved_arrangement.rename({'title':'Title'},axis=1)
        df_resolved_sessions = df_raw_session.merge(df_resolved_arrangement,how='left', left_on='l_arrangement_id', right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id'},axis=1)
        df_resolved_sessions['Session Date'] = pd.to_datetime(df_resolved_sessions['session_date']).dt.strftime("%m/%d/%Y")
        df_resolved_sessions = df_resolved_sessions.merge(df_raw_guitar,how='left', left_on='guitar_id',right_on='id').drop(['id_y'],axis=1).rename({'id_x':'id'}, axis=1)
        df_resolved_sessions = df_resolved_sessions.rename({'duration':'Duration','notes':'Notes','Title':'Song','video_url':'Video URL','make':'Guitar Make','model':'Guitar Model'},axis=1)
        df_resolved_sessions = df_resolved_sessions.sort_values('session_date', ascending=False)
        self.df_summary = df_resolved_sessions[['id', 'Session Date', 'Duration', 'Song','Composer','Arranger','Notes', 'Video URL', 'Guitar Make', 'Guitar Model']]
        
        # Establish arrangement lookup
        df_sessions_copy = df_resolved_sessions.copy()
        df_resolved_sessions = df_resolved_sessions.drop('l_arrangement_id',axis=1)
        df_sessions_copy['session_date'] = pd.to_datetime(df_sessions_copy['session_date'])
        df_sessions_copy['Lookup Name'] = df_sessions_copy.apply(lambda row: str(row['Song'])+' ('+str(row['last_name_x'])+'/'+str(row['last_name_y'])+")", axis=1)
        df_resolved_arrangement['Lookup Name'] = df_resolved_arrangement.apply(lambda row: str(row['Title'])+' ('+str(row['last_name_x'])+'/'+str(row['last_name_y'])+")", axis=1)
        
        # Isolate songs played in last 10 days and order by session_date descending / then alphabetical ascending
        df_arrangements_last_ten_days =df_sessions_copy[df_sessions_copy['session_date']>=datetime.datetime.now() - pd.DateOffset(days=10)].sort_values('session_date',ascending=False).drop_duplicates('Lookup Name', keep='first')
        df_arrangements_last_ten_days = df_arrangements_last_ten_days.sort_values(['session_date','last_name_x'], ascending = [False,True])
        df_arrangements_last_ten_days = df_arrangements_last_ten_days[['l_arrangement_id','Lookup Name']]

        # order remaining arrangements by total time played descending
        df_arrangements_ordered_by_playtime = df_sessions_copy.groupby('Lookup Name')['Duration'].sum().sort_values(ascending=False).reset_index(drop=False)
        df_arrangements_ordered_by_playtime = df_arrangements_ordered_by_playtime[~df_arrangements_ordered_by_playtime['Lookup Name'].isin(list(df_arrangements_last_ten_days['Lookup Name']))] # Remove records played in last ten days
        df_arrangements_ordered_by_playtime = df_arrangements_ordered_by_playtime.merge(df_resolved_arrangement[['id','Lookup Name']], how='inner', on='Lookup Name').rename({'id':'l_arrangement_id'},axis=1)

        df_arrangement_lookup = pd.concat([df_arrangements_last_ten_days, df_arrangements_ordered_by_playtime]).reset_index(drop=True)
        df_resolved_arrangement = df_resolved_arrangement.sort_values('last_name_x').rename({'id':'l_arrangement_id'},axis=1)[['l_arrangement_id','Lookup Name']]
        
        df_unplayed_arrangements = df_resolved_arrangement[~df_resolved_arrangement['Lookup Name'].isin(list(df_arrangement_lookup['Lookup Name']))]
        df_arrangement_lookup = pd.concat([df_arrangement_lookup, df_unplayed_arrangements]).reset_index(drop=True)
        
        self.__arrangement_lookup = {'':''}
        self.__arrangement_lookup.update({value:f"{lookup_name}" for value,lookup_name in zip(df_arrangement_lookup['l_arrangement_id'],df_arrangement_lookup['Lookup Name'])})

        df_temp_raw_guitar = df_raw_guitar.copy()
        df_temp_raw_guitar['default_msg'] = np.where(df_raw_guitar['default_guitar']," (Default)","")
        self.__guitar_lookup = {'':''}
        self.__guitar_lookup.update({value:f"{make} - {model}{def_msg}" for value,make,model,def_msg in zip(df_temp_raw_guitar['id'],df_temp_raw_guitar['make'],df_temp_raw_guitar['model'], df_temp_raw_guitar['default_msg'])})

        def_guitar_ids = df_raw_guitar[df_raw_guitar['default_guitar']==True]['id'].values
        if len(def_guitar_ids>0):
            self.__default_guitar_id=def_guitar_ids[0]


    def __init_session_date(self):
        # provide initial value for the startsession date on the input form
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

    def __init_arrangement(self):
        # provide initial value for the lookup field of the input form
        if self._df_selected_id:
            # User selected Update
            arrangement_id = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['l_arrangement_id'].values[0]
            if (arrangement_id):
                if (not math.isnan(arrangement_id)):
                    return int(arrangement_id) # Update a record with a non-null selection
                    '' # Update a record with a null id
            else:
                return '' # Update a record with a null id
        else:
            # User selected New
            return '' # New Record, there is no value     
  
    def __init_guitar(self):
        # provide initial value for the lookup field of the input form
        if self._df_selected_id:
            # User selected Update
            guitar_id = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['guitar_id'].values[0]
            if (guitar_id):
                if (not math.isnan(guitar_id)):
                    return int(guitar_id) # Update a record with a non-null selection
                    '' # Update a record with a null id
            else:
                return '' # Update a record with a null id
        else:
            # User selected New
            if self._SessionInputTableModel__default_guitar_id is not None:
                # pre-populate with default guitar
                return int(self._SessionInputTableModel__default_guitar_id)
            else:
                return '' # New Record - no default guitar selected, there is no value     
  

    def __init_duration(self):
        # provide initial value for the duration field of the input form
        if self._df_selected_id:
            return int(self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['duration'].values[0])
        else:
            # User selected New
            return None
        
    def __init_notes(self):
        # provide initial value for the notes field of the input form
        if self._df_selected_id:
            return self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['notes'].values[0]
        else:
            # User selected New
            return None        

    def __init_video_url(self):
        # provide initial value for the video url field of the input form
        if self._df_selected_id:
            return self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['video_url'].values[0]
        else:
            # User selected New
            return None 

    def _ui_specific_code(self):
        """
        Arrangement Modal Form UI code goes here
        """
        return ui.row(
            ui.div(self._init_id_text()),
            ui.input_date(id="session_date",label=f"Session Date *", value=self.__init_session_date()).add_style('color:red;'), #REQUIRED FIELD
            ui.input_text(id="duration",label="Duration *", value=self.__init_duration()).add_style('color:red;'), #REQUIRED FIELD
            ui.input_select(id="arrangement_id",label="Arrangement *",choices=self.__arrangement_lookup, selected=self.__init_arrangement()).add_style('color:red;'), #REQUIRED FIELD
            ui.input_text_area(id="notes", label="Session Notes",value=self.__init_notes()),
            ui.input_text(id="video_url", label="Video Url (YouTube)",value=self.__init_video_url()),
            ui.input_select(id="guitar_id",label="Guitar Used *",choices=self.__guitar_lookup, selected=self.__init_guitar()).add_style('color:red;'), #REQUIRED FIELD
        ),

    def server_call(self, input, output, session, summary_df):
        """
        Arrangement Modal Form Server code goes here
        """

        @module.server
        def input_form_func(input, output, session, summary_df):

            output_name = reactive.value('')
            data_validation_msg = reactive.value('')

            @reactive.effect
            @reactive.event(input.btn_input_form_submit, ignore_init=True, ignore_none=True)
            def triggerInputFormSubmit():
                # Perform Data Validation and msg if issues
                try:
                    req(input.session_date())
                    req(input.guitar_id())
                    req(input.duration())
                    req(input.arrangement_id())
                except:
                    data_validation_msg.set('Please fill in all required form fields!')
                    return
                else:
                    data_validation_msg.set('')



                # Data Validation Passed - Write database row

                # Determine the Stage of progress:
                # Binary Tree to speed up stage classification
                #
                #                        at_tempo_date
                #                       /            \
                #           off_book_date             play_ready_date
                #          /            \             /              \
                #     "Learning     "Achieving     "Phrasing"       "Maintenance"
                #        Notes"        Tempo"

                df_arrangements = self._SessionInputTableModel__db_arrangement_model.df_raw
                arrangement_id = None if input.arrangement_id() == '' else input.arrangement_id()
                ser_this_arrangement = df_arrangements[df_arrangements['id']==int(arrangement_id)].iloc[0]
                session_date = input.session_date()
                stage=''
                if ser_this_arrangement['at_tempo_date']:
                    if session_date>=ser_this_arrangement['at_tempo_date']:
                        # Test against play_ready_date
                        if ser_this_arrangement['play_ready_date']:
                            if session_date>=ser_this_arrangement['play_ready_date']:
                                stage='Maintenance'
                            else:
                                stage='Phrasing'
                        else:
                            stage='Phrasing'
                    else:
                        # session_date is < at_tempo_date.  test off_book_date
                        if ser_this_arrangement['off_book_date']:
                            if session_date>=ser_this_arrangement['off_book_date']:
                                stage="Achieving Tempo"
                            else:
                                stage="Learning Notes"
                        else:
                            stage="Learning Notes"
                else:
                    #   test off_book_date
                    if ser_this_arrangement['off_book_date']:
                        if session_date>=ser_this_arrangement['off_book_date']:
                            stage="Achieving Tempo"
                        else:
                            stage="Learning Notes"
                    else:
                        stage="Learning Notes"
                    # at_tempo_date doesn't exist. Test off_book_date


                
                                
                
                # Create single row as dataframe
                df_row_to_database = pd.DataFrame({'id':[self._df_selected_id],
                                                'session_date':[input.session_date()],
                                                'duration':[input.duration()],
                                                'l_arrangement_id':[arrangement_id],
                                                'notes':[input.notes()],
                                                'video_url':[input.video_url()],
                                                'guitar_id':[input.guitar_id()],
                                                'stage':[stage]})
                if self._df_selected_id:
                    self._db_table_model.update(df_row_to_database)
                else:
                    self._db_table_model.insert(df_row_to_database)
                
                ui.modal_remove()
                self.processData()
                summary_df.set(self.df_summary)
           
            @reactive.effect
            @reactive.event(input.btn_input_cancel)
            def triggerInputCancel():
                ui.modal_remove()

            @render.text
            def data_validation_text():
                return data_validation_msg()

            return self.df_summary.copy

        return input_form_func(self._namespace_id, summary_df)

