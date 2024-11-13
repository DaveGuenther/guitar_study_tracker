# Core

from datetime import date
import pandas as pd

# Utility
import logger

# Web/Visual frameworks
from shiny import ui, module
import plotly.graph_objects as go
import plotly.express as px
from shinywidgets import output_widget, render_widget, render_plotly

# App Specific Code
import global_data
globals = global_data.GlobalData()

Logger = logger.FunctionLogger


df_sessions = globals.get_df_sessions()
df_grindage = globals.get_df_song_grindage()

def timestamp_to_date(this_timestamp: pd._libs.tslibs.timestamps._Timestamp):
    return date(this_timestamp.year, this_timestamp.month, this_timestamp.day)

@module.ui
def career_ui():

    def filter_shelf(df):
        return ui.div(
            ui.input_date_range(
                id='daterange',
                label='Date Range',
                start=timestamp_to_date(df['session_date'].min()),
                end=timestamp_to_date(df['session_date'].max()),
            ),
        )
    
    ret_val = ui.nav_panel("Career",
        "Career",
        ui.sidebar(
            ui.h4("Filters"),
            filter_shelf(df_sessions),
            width=300,
        ),
        ui.card(
            output_widget(id='song_grindage_chart')
        ).add_class('dashboard-card'),
        ui.row(
            ui.column(3,
                ui.card(
                    ui.h4("Avg. Practice Time/Day"),

                ),
            ),
            ui.column(2,
                ui.card(
                    ui.h4("Longest Practice Streak"),

                ),                        

            ),
            ui.column(2,
                ui.card(
                    ui.h4("Longest Session"),

                ),
            ),
            ui.column(3,
                ui.card(
                    ui.h4("Total Career Practice Time"),

                ),
            ),
            ui.column(2,
                ui.card(
                    ui.h4("Year:"),

                ),
            ),                                                                                                
        ),
    )

    return ret_val

@module.server
def career_server(input, output, session):
    Logger(session.ns)

    @render_widget
    def song_grindage_chart():
        print("Hello")

        # Unused Code - Just to figure out way to calculate x, y, and color for bar traces for any dataframe
        for color in df_grindage['Stage'].unique():
            print(list(df_grindage[df_grindage['Stage']==color]['Title']))
            print(list(df_grindage[df_grindage['Stage']==color]['Duration']))


        fig = px.bar(
            df_grindage, 
            x='Duration',
            y='Title',
            color='Stage',
            title='Repertoire Progress',

            

        )

#        fig.update_layout(
            
#            title=dict(text="Repertoire Progress",font=dict(size=30, color="#FFF8DC"),yanchor='bottom', yref='paper'),
#            xaxis_side='bottom',
#            xaxis_dtick=1, 
            
            # Main plot styling
#            font_family='garamond',            
#            font_color='#Ff9b15',
#            paper_bgcolor='rgba(0, 0, 0, 0)',
            
#            xaxis_tickfont=dict(size=14),
#            yaxis_tickfont=dict(size=14),

#            yaxis_dtick=1,
#            plot_bgcolor="#40291D",        
#        )
        figWidget = go.FigureWidget(fig)
        return figWidget
        
    
        