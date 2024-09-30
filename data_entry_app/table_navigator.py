# core
import pandas as pd
from abc import ABC, abstractmethod

# Web/Visual Frameworks
from shiny import module, reactive, render, ui, req

# Web App Specific
import data_processing

class ShinyFormTemplate:
    _namespace_id = None
    _form_data=None
    
    def __init__(self, namespace_id:str, form_data:data_processing.ShinyInputTableModel):
        """
        _namespace_id (str):            This is the id value of the namespace that the form's shiny module will use.  It will prefix the id value of every applicable component on the DOM
        _df_form_data (pd.DataFrame):   This is the dataframe that can either be used to populate the form data as it would be 

        """
        self._namespace_id=namespace_id
        self._form_data=form_data

    def ui_call(self):
        @module.ui
        def nav_ui():
            return ui.row(
                ui.row(ui.column(4, ui.div(id=f"{self._namespace_id}_btn_update_placeholder")),
                    ui.column(4),
                    ui.column(4, ui.input_action_button(
                        "btn_new", "New", width="100%")),
                    ),
                ui.output_data_frame("summary_table"),
                ui.div(id=f"{self._namespace_id}_modal_ui_placeholder")
            )
        return nav_ui(self._namespace_id)

    def server_call(self, input, output, session):

        @module.server
        def nav_server(input, output,session):
            updateButtonVisible = reactive.value(False)
            df_selected_row = reactive.value(pd.DataFrame()) # Single Row dataframe of the selected row in the summary table
            df_selected_id=reactive.value(None) # id value of the selected row
            df_summary=reactive.value(self._form_data.df_summary.copy()) # This reactive is updated upon completion of input form modal to refresh the navigator window with newly adjusted data

            ## Renders the summary dataframe for the nav_panel
            @render.data_frame
            def summary_table():
                return render.DataGrid(
                df_summary(),
                width="100%",
                height="100%",
                selection_mode="row"
            )

            ## Stores the ID of the selected table row in reactive val
            @reactive.effect
            @reactive.event(df_selected_row)
            def setSelectedID():
                if df_selected_row().shape[0]>0:
                    df_selected_id.set(df_selected_row()['id'].values[0])
                else:
                    df_selected_id.set(None)

            ## Update Button Click Event
            @reactive.effect
            @reactive.event(input.btn_update)
            def triggerUpdateButton():
                # Execute Module UI and Server code together
                # UI first
                ui.insert_ui(self._form_data.ui_call(df_selected_id()), 
                             selector=f"#{self._namespace_id}_modal_ui_placeholder", 
                             where="beforeBegin")
                
                #Server (notice that we pass in df_summary as reactive value to force redraw the table when the modal is closed)
                ui.remove_ui(f"#{self._namespace_id}-btn_update") # Hide Update Button
                self._form_data.server_call(input,output,session, df_summary)
                updateButtonVisible.set(False)
                df_selected_row.set(pd.DataFrame())
                df_selected_id.set(None)        
                #summary_table.update_cell_selection(selection='none')

            ## New Button Click Event
            @reactive.effect
            @reactive.event(input.btn_new)
            def triggerNewButton():
                ui.insert_ui(self._form_data.ui_call(None), 
                             selector=f"#{self._namespace_id}_modal_ui_placeholder", 
                             where="beforeBegin")
                self._form_data.server_call(input,output,session, df_summary)
                updateButtonVisible.set(False)
                df_selected_row.set(pd.DataFrame())
                df_selected_id.set(None)

            ## Shows Update Button (when a table row is selected)
            @reactive.effect
            def insert_update_button():
                data_selected = summary_table.data_view(selected=True) 
                df_selected_row.set(data_selected.copy())
                req(not (data_selected.empty or updateButtonVisible.get()))
                ui.insert_ui(
                    ui.input_action_button("btn_update",
                                        "Update", width='100%'),
                    selector=f"#{self._namespace_id}_btn_update_placeholder",
                    where="beforeBegin"
                )
                updateButtonVisible.set(True)
        
        # This must be here (calls the server module within the method)
        return nav_server(self._namespace_id)



