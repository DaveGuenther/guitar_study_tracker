# Core
import pandas as pd

# Web/Visual frameworks
from shiny import App, ui, render, reactive, types, req

# Shiny App Specific
import database as db

app_ui = ui.page_fluid(
    ui.page_navbar(
        ui.nav_panel("New Practice Session", "New Practice Session - Input Form",
                     ui.row(
                         ui.row(ui.column(2, ui.div(id="placeholder")),
                                ui.column(8),
                                ui.column(2, ui.input_action_button(
                                    "btn_new_session", "New", width="100%")),
                                ),
                         ui.output_data_frame("session_summary")
                     )),
        ui.nav_panel("New Song", "New Song - Input Form",
                     "Song"),
        ui.nav_panel("New Artist", "New Artist - Input Form",
                     "Artist"),
        title="Guitar Study Tracker",
        id="page",
    ),
    ui.output_ui('page_manager'),
)

def server(input, output, session):
    
    updateButtonVisible = reactive.value(False)
    df_selected_row = reactive.value(pd.DataFrame())
    

    def nav_song():
        return "Song"

    def nav_artist():
        return "Artist"

    @render.data_frame
    def session_summary():
        return render.DataGrid(
            db.df_summary_practice_sessions,
            width="100%",
            height="100%",
            selection_mode="rows"
        )

    @reactive.effect
    def insert_update_button():
        data_selected = session_summary.data_view(selected=True)
        req(not (data_selected.empty or updateButtonVisible.get()))
        ui.insert_ui(
            ui.input_action_button("btn_update_session",
                                   "Update", width='100%'),
            selector="#placeholder",
            where="beforeBegin"
        )
        updateButtonVisible.set(True)
        df_selected_row.set(data_selected.copy())

    @render.ui
    def page_manager():
        if input.page() == "New Song":
            return nav_song()
        if input.page() == "New Artist":
            return nav_artist()
        return None

        
app = App(app_ui, server)
