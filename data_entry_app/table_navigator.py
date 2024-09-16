# core
import pandas as pd

# Web/Visual Frameworks
from shiny import module, reactive, render, ui, req

# Web App Specific
import data_processing

@module.ui
def nav_ui(shiny_data_payload:data_processing.ShinyTableModel):
    return ui.row(
        ui.row(ui.column(2, ui.div(id=f"{shiny_data_payload.id}_btn_update_placeholder")),
            ui.column(8),
            ui.column(2, ui.input_action_button(
                "btn_new", "New", width="100%")),
            ),
        ui.output_data_frame("summary_table")
    )

@module.server
def nav_server(input, output, session, shiny_data_payload:data_processing.ShinyTableModel):
    """
        input, output, session:             Standard Shiny objects
        prefix (str):                       Name to add to add to div ids to keep them unique in the ui
        df_summary (pd.DataFrame):          Summarized view of the database table to show in the navigator
    """

    updateButtonVisible = reactive.value(False)
    df_selected_row = reactive.value(pd.DataFrame())

    @render.data_frame
    def summary_table():
        return render.DataGrid(
            shiny_data_payload.df_resolved[shiny_data_payload.summary_columns],
            width="100%",
            height="100%",
            selection_mode="row"
        )


    @reactive.effect
    def insert_update_button():
        data_selected = summary_table.data_view(selected=True)
        req(not (data_selected.empty or updateButtonVisible.get()))
        ui.insert_ui(
            ui.input_action_button("btn_update",
                                   "Update", width='100%'),
            selector=f"#{shiny_data_payload.id}_btn_update_placeholder",
            where="beforeBegin"
        )
        updateButtonVisible.set(True)
        df_selected_row.set(data_selected.copy())
