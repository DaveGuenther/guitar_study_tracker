class ShinyInputTableModel(ABC):
    """
    This class will make use of DatabaseTableModels to establish more complete table representation for user form input (including where necessary bringing in lookup tables to resolve lookup ids in the primary table).  It also contains specific UI components required for the inpurt form modal.
    """

    _namespace_id=None # used as prefix for the shiny module (e.g. 'artist','arrangement')

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
                    ui.column(4, ui.input_action_button("btn_input_form_submit", "Submit", width="100%", disabled=self._db_table_model.isReadOnly())),
                ),
                title=f"Input Form - New {self._title}",
                easy_close=True,
                footer=None,
            )
            return ui.modal_show(input_form_modal)

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

