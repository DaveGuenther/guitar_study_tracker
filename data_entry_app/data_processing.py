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
           
            @reactive.effect
            @reactive.event(input.btn_input_cancel)
            def triggerInputCancel():
                ui.modal_remove()

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
            # provide initial value for the name field of the input form
            return str(self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['hyperlink'].values[0])
        else:
            return None

    def __init_image_url(self):
        if self._df_selected_id:
            # provide initial value for the name field of the input form
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
            
            @reactive.effect
            @reactive.event(input.btn_input_form_submit, ignore_init=True, ignore_none=True)
            def triggerInputFormSubmit():
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
            
            @reactive.effect
            @reactive.event(input.btn_input_form_submit, ignore_init=True, ignore_none=True)
            def triggerInputFormSubmit():
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
        df_raw_song['composer'] = df_raw_song['composer'].astype("Int64") # Allows us to join on null ints since this column is nullable
        df_raw_song['arranger'] = df_raw_song['arranger'].astype("Int64") # Allows us to join on null ints since this column is nullable
        df_resolved_song = df_raw_song.merge(df_raw_artist, how='left', left_on='arranger', right_on='id').drop(['arranger','id_y','last_name'],axis=1).rename({'id_x':'id','name':'Arranger'},axis=1)
        df_resolved_song = df_resolved_song.merge(df_raw_artist, how='left', left_on='composer', right_on='id').drop(['composer','id_y'],axis=1).rename({'id_x':'id','name':'Composer'},axis=1)
        df_resolved_song = df_resolved_song.merge(df_raw_style, how='left', left_on='style_id', right_on='id').drop(['style_id','id_y'], axis=1).rename({'id_x':'id', 'style':'Style'},axis=1)
        df_resolved_song['Start Date'] = pd.to_datetime(df_resolved_song['start_date']).dt.strftime("%m/%d/%Y")
        df_resolved_song['At Tempo Date'] = pd.to_datetime(df_resolved_song['at_tempo_date']).dt.strftime("%m/%d/%Y")
        df_resolved_song['Off Book Date'] = pd.to_datetime(df_resolved_song['off_book_date']).dt.strftime("%m/%d/%Y")
        df_resolved_song['Play Ready Date'] = pd.to_datetime(df_resolved_song['play_ready_date']).dt.strftime("%m/%d/%Y")
        df_resolved_song = df_resolved_song.rename({'title':'Title', 'song_type':'Song Type'},axis=1).sort_values(['last_name','Title'])
        self.df_summary = df_resolved_song[['id','Title','Composer','Song Type','Style','Start Date','Off Book Date','At Tempo Date','Play Ready Date']]


        # Establish artist lookup
        self.__artist_lookup = {'':''}
        self.__artist_lookup.update({value:label for value,label in zip(df_raw_artist['id'],df_raw_artist['name'])})
        
        # Establish style lookup
        self.__style_lookup = {'':''}
        self.__style_lookup.update({value:label for value,label in zip(df_raw_style['id'],df_raw_style['style'])})

        

        

    def __init_title(self):
        # provide initial value for the name field of the input form
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
        # provide initial value for the arranger lookup field of the input form
        if self._df_selected_id: 
            # User selected Update
            artist_id = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['composer'].values[0]
            if pd.isna(artist_id):
                return '' # Update a record with a null artist id

            else:
                if (not math.isnan(artist_id)):
                    return int(artist_id) # Update a record with a non-null artist selection
                '' # Update a record with a null artist id
        else:
            # User selected New
            return '' # New Record, there is no value   
  

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



    def __init_style(self):
        # provide initial value for the arranger lookup field of the input form
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
        Song Modal Form UI code goes here
        """
        return ui.row(
            ui.div(self._init_id_text()),
            ui.input_text(id="title",label=f"{self._title} Title *", value=self.__init_title()).add_style('color:red;'), # REQUIRED VALUE
            ui.input_select(id='song_type', label="Song Type", choices=self.__song_type_lookup, selected=self.__init_song_type()),
            ui.input_select(id='style',label="Style", choices=self.__style_lookup, selected=self.__init_style()),
            ui.input_select(id="composer",label="Composer",choices=self.__artist_lookup, selected=self.__init_composer()),
            ui.input_select(id="arranger",label="Arranger",choices=self.__artist_lookup, selected=self.__init_arranger()),
            ui.input_date(id="start_date", label="Start Date",value=self.__init_start_date()),
            ui.input_date(id="off_book_date", label="Off Book Date",value=self.__init_off_book_date()),
            ui.input_date(id="at_tempo_date", label="At Tempo Date",value=self.__init_at_tempo_date()),            
            ui.input_date(id="play_ready_date", label="Play Ready Date",value=self.__init_play_ready_date()),
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
                #print("Inside Submit")
                composer_id = None if input.composer() == '' else input.composer()
                arranger_id = None if input.arranger() == '' else input.arranger()
                style_id = None if input.style() == '' else input.style()
                song_type = None if input.song_type() == '' else input.song_type()
                # Create single row as dataframe
                df_row_to_database = pd.DataFrame({'id':[self._df_selected_id],
                                                   'title':[input.title()], # REQUIRED VALUE
                                                   'style_id':[style_id],
                                                   'composer':[composer_id],
                                                   'arranger':[arranger_id],
                                                   'start_date':[input.start_date()],
                                                   'off_book_date':[input.off_book_date()],
                                                   'at_tempo_date':[input.at_tempo_date()],
                                                   'play_ready_date':[input.play_ready_date()],
                                                   'song_type':[song_type]})
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

            return self.df_summary.copy

        return input_form_func(self._namespace_id, summary_df)


class SongGoalInputTableModel(ShinyInputTableModel):    

    __db_song_model=None
    __db_artist_model=None

    # We want the lookup control for songs on the form to show all songs on the songs table that aren't already on the goal songs table.
    # However, when we update an existing goal song record, we also want to add that song id to the song lookup table for that instance of the modal so that is isn't blank when we click Update on the record.
    __song_lookup={}  # Gets populated during _ui_specific_code() so that it can have dynamic values for Update records
    __df_resolved_song=pd.DataFrame() # used to add a selected id to the song lookup table when a user clicks on update

    def __init__(self, namespace_id:str, title:str, db_table_model:database.DatabaseModel, db_song_model:database.DatabaseModel, db_artist_model:database.DatabaseModel):
        self._namespace_id=namespace_id
        self._title=title
        self._db_table_model=db_table_model
        self.__db_song_model = db_song_model
        self.__db_artist_model = db_artist_model

    def processData(self):
        # There is more complex logic required to process the Song dataframe because it has the artist lookup field to worry about
        df_raw_song_goal = self._db_table_model.df_raw
        df_raw_artist = self.__db_artist_model.df_raw
        df_raw_song = self.__db_song_model.df_raw
        
        df_raw_song['composer'] = df_raw_song['composer'].astype("Int64") # Allows us to join on null ints since this column is nullable
        df_raw_song['arranger'] = df_raw_song['arranger'].astype("Int64") # Allows us to join on null ints since this column is nullable
        df_resolved_song = df_raw_song.merge(df_raw_artist, how='left', left_on='arranger', right_on='id').drop(['arranger','id_y','last_name'],axis=1).rename({'id_x':'id','name':'Arranger'},axis=1)
        df_resolved_song = df_resolved_song.merge(df_raw_artist, how='left', left_on='composer', right_on='id').drop(['composer','id_y'],axis=1).rename({'id_x':'id','name':'Composer'},axis=1)
        self.__df_resolved_song=df_resolved_song.copy()
        df_resolved_song_goal = df_raw_song_goal.merge(df_resolved_song, how='left', left_on='song_id', right_on='id').drop(['id_y'], axis=1).rename({'id_x':'id'}, axis=1)
        #df_resolved_song_goal = df_resolved_song.merge(df_raw_song_goal, left_on='id', right_on='song_id', how='right').drop(['id_y'], axis=1).rename({'id_x':'id'}, axis=1)
        df_resolved_song['Start Date'] = pd.to_datetime(df_resolved_song['start_date']).dt.strftime("%m/%d/%Y")

        # Build rendered dataframe for the table navigator
        df_summary = df_resolved_song_goal.rename({'title':'Title', 'song_type':'Song Type','description':'Description','discovery_date':'Date Discovered'},axis=1).sort_values(['Date Discovered'], ascending=False)
        df_summary['Date Discovered'] = pd.to_datetime(df_summary['Date Discovered']).dt.strftime("%m/%d/%Y")
        self.df_summary = df_summary[['id','Title','Composer','Arranger','Date Discovered','Description']]


        # Establish song lookup for the song goals table
        song_ids_on_goals_table = df_resolved_song_goal['song_id']
        df_song_lookup = df_resolved_song[~df_resolved_song['id'].isin(song_ids_on_goals_table)] # Songs from the song table can only be added once to the goal table
        self.__new_song_lookup = {'':''}
        self.__new_song_lookup.update({value:str("Composer: "+str(composer)+", Song: "+str(title)+', Arranger: '+str(arranger)) for value,composer,arranger,title in zip(df_song_lookup['id'],df_song_lookup['Composer'],df_song_lookup['Arranger'],df_song_lookup['title'])})   


        

    def __init_description(self):
        # provide initial value for the description field of the input form
        if self._df_selected_id:
            return str(self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['description'].values[0])
        else:
            # User selected New
            return None     

    def __init_song(self):
        # provide initial value for the song lookup field of the input form
        if self._df_selected_id: 
            # User selected Update
            song_id = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['song_id'].values[0]
            if pd.isna(song_id):
                return '' # Update a record with a null song id

            else:
                if (not math.isnan(song_id)):
                    return int(song_id) # Update a record with a non-null song selection
                '' # Update a record with a null song id
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
        Song Goal Modal Form UI code goes here.
        """
        ###  This function is called from the Parent Abstract Class ShinyInputTableModel.  In order to addess private members from this child class, instead of using self.__value, we have to 
        ###  deliberately access the child's provate data from the parent class: self._SongGoalInputTableModel__value.  I'm not exactly sure why, but python isn't able to resolve self.__value
        ###  in this function when it is called from the parent class.
        df_resolved_song = self._SongGoalInputTableModel__df_resolved_song # pseudonym for self.__df_resolved_song.
        self._SongGoalInputTableModel__song_lookup=self._SongGoalInputTableModel__new_song_lookup # pesudonym for self.__new_song_lookup.  Lookup song control contains only songs that aren't on the gosl song table.
        if self._df_selected_id:
            # Add a record to the lookup song control for the selected song_id so that it shows when a form is updated
            song_id = self._db_table_model.df_raw[self._db_table_model.df_raw['id']==self._df_selected_id]['song_id'].values[0]
            composer=df_resolved_song[df_resolved_song['id']==song_id]['Composer'].values[0]
            arranger=df_resolved_song[df_resolved_song['id']==song_id]['Arranger'].values[0]
            title=df_resolved_song[df_resolved_song['id']==song_id]['title'].values[0]
            self._SongGoalInputTableModel__song_lookup.update({int(song_id):str("Composer: "+str(composer)+", Song: "+str(title)+', Arranger: '+str(arranger))})
            

        return ui.row(
            ui.div(self._init_id_text()),
            ui.input_select(id='song_id', label="Select a Song *", choices=self.__song_lookup, selected=self.__init_song()).add_style('color:red;'), # REQUIRED VALUE
            ui.input_text(id="description",label="Song Description/Inspiration", value=self.__init_description()), 
            ui.input_date(id="discovery_date", label="Date Discovered",value=self.__init_discovery_date()).add_style('color:red;'), # REQUIRED VALUE
        ),

    def server_call(self, input, output, session, summary_df):
        """
        Song Goal Modal Form Server code goes here
        """

        @module.server
        def input_form_func(input, output, session, summary_df):

            output_name = reactive.value('')
            
            @reactive.effect
            @reactive.event(input.btn_input_form_submit, ignore_init=True, ignore_none=True)
            def triggerInputFormSubmit():
                #print("Inside Submit")
                song_id = None if input.song_id() == '' else input.song_id()
                # Create single row as dataframe
                df_row_to_database = pd.DataFrame({'id':[self._df_selected_id],
                                                   'song_id':[song_id], # REQUIRED VALUE
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

            return self.df_summary.copy

        return input_form_func(self._namespace_id, summary_df)


class SessionInputTableModel(ShinyInputTableModel):    

    __db_artist_model=None
    __db_song_model=None
    __song_lookup=None
    __guitar_lookup=None

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
        df_song_lookup = df_raw_song.merge(df_raw_artist,how='left',left_on='composer',right_on='id')
        df_song_lookup = df_song_lookup.rename({'id_x':'id'},axis=1).drop('id_y',axis=1)
        df_song_lookup['last_name']=df_song_lookup['name'].str.split(' ').str[-1].fillna('Unknown')
        df_song_lookup = df_song_lookup.sort_values(['last_name','title'])
        self.__song_lookup = {'':''}
        self.__song_lookup.update({value:f"{artist} - {label}" for value,label,artist in zip(df_song_lookup['id'],df_song_lookup['title'],df_song_lookup['last_name'])})

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
            ui.div(self._init_id_text()),
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
                print(f"Input button value [{input.btn_input_form_submit()}]")
                print("Input Submit Pressed!")
                song_id = None if input.song_id() == '' else input.song_id()
                # Create single row as dataframe
                df_row_to_database = pd.DataFrame({'id':[self._df_selected_id],
                                                'session_date':[input.session_date()],
                                                'duration':[input.duration()],
                                                'l_song_id':[song_id],
                                                'notes':[input.notes()],
                                                'video_url':[input.video_url()]})
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

            return self.df_summary.copy

        return input_form_func(self._namespace_id, summary_df)

