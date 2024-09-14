# Core
import pandas as pd

# Web/Visual frameworks
from shiny import App, ui, render, reactive, types, req, module

# Shiny App Specific
import database as db

@module.ui
def table_navigator_ui(prefix):
    return ui.row(
        ui.row(ui.column(2, ui.div(id=f"{prefix}_btn_update_placeholder")),
            ui.column(8),
            ui.column(2, ui.input_action_button(
                "btn_new", "New", width="100%")),
            ),
        ui.output_data_frame("summary_table")
    )

@module.server
def table_navigator_server(input, output, session, prefix, df):
    updateButtonVisible = reactive.value(False)
    df_selected_row = reactive.value(pd.DataFrame())

    @render.data_frame
    def summary_table():
        return render.DataGrid(
            df,
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
            selector=f"#{prefix}_btn_update_placeholder",
            where="beforeBegin"
        )
        updateButtonVisible.set(True)
        df_selected_row.set(data_selected.copy())

app_ui = ui.page_fluid(
    ui.page_navbar(
        ui.nav_panel("New Practice Session", "New Practice Session - Input Form",
            table_navigator_ui(id="practice_session", prefix="practice_session")),            
        ui.nav_panel("New Song", "New Song - Input Form",
            table_navigator_ui("song", prefix="song")),
        ui.nav_panel("New Artist", "New Artist - Input Form",
            table_navigator_ui("artist", prefix="artist")),
        title="Guitar Study Tracker",
        id="page",
    ),
    ui.output_ui('page_manager'),
)

def server(input, output, session):
    
    table_navigator_server("practice_session", prefix="practice_session", df=db.df_summary_practice_sessions)
    table_navigator_server("song", prefix="song", df=db.df_summary_songs)
    table_navigator_server("artist", prefix="artist", df=db.df_summary_artists)    
        
app = App(app_ui, server)
