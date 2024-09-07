
# Web/Visual frameworks
from shiny import App, ui, render

# Shiny App Specific
import database as db

app_ui = ui.page_fluid(
    ui.page_navbar(
        ui.nav_panel("New Practice Session", "New Practice Session - Input Form"),
        ui.nav_panel("New Song", "New Song - Input Form"),
        ui.nav_panel("New Artist", "New Artist - Input Form"),
        title="Guitar Study Tracker",
        id="page",
    ),
    ui.output_ui('page_manager'),
)

def server(input, output, session):
    
    @render.data_frame
    def session_summary():
        return render.DataGrid(
            db.df_summary_practice_sessions,
            width="100%",
            height="100%",
            selection_mode="row"
        )

    def nav_practice_session():
        ret_ui = ui.row(
            ui.output_data_frame("session_summary")
        )
        return ret_ui

    def nav_song():
        return "Song"

    def nav_artist():
        return "Artist"

    @render.ui
    def page_manager():
        if input.page()=="New Practice Session":
            return nav_practice_session() 
        if input.page()=="New Song":
            return nav_song()
        if input.page()=="New Artist":
            return nav_artist()
        return None
        
app = App(app_ui, server)
