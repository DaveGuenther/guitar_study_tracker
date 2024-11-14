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

        def make_traces(df_in, dimension_a, dimension_b, field_3, dimension_a_sort_order=None, dimension_b_sort_order=None):
            """
            dimension_a, dimension_b  (str): column name of a dimension in the incoming dataframe.  These will be the rows and columns of the matrix that is built.
            field_3 (str): column name of a measure or dimension in the dataframe who's value will be isolated in the intersection of dimension_a and dimension_b.
            dimension_a_sort_order (list)
            """
            if dimension_a_sort_order:
                df_in[dimension_a] = pd.Categorical(df_in[dimension_a], categories=dimension_a_sort_order, ordered=True)
            if dimension_b_sort_order:
                df_in[dimension_b] = pd.Categorical(df_in[dimension_b], categories=dimension_b_sort_order, ordered=True)
            df_in = df_in.sort_values([dimension_a,dimension_b])
            df_in_pivot = df_in.pivot(columns=[dimension_a],index=[dimension_b])
            dim_a_vals = list(df_in[dimension_a].unique())
            dim_b_vals = list(df_in_pivot.index)
            dim_c_vals=[]
            for dim_b in dim_b_vals:
                dim_c_vals.append(list(df_in_pivot.loc[dim_b][field_3].fillna(0)))
            return dim_a_vals, dim_c_vals
            

        stage_order = ['Learning Notes','Achieving Tempo','Phrasing','Maintenance']
        title_order = list(df_grindage.groupby('Title')['Duration'].sum().sort_values(ascending=False).index)
        title_vals, duration_vals = make_traces(df_grindage, 'Title', 'Stage','Duration', dimension_a_sort_order=title_order, dimension_b_sort_order=stage_order)
        
        data = [go.Bar(name=color, x = title_vals, y=duration) for color,duration in zip(stage_order,duration_vals)]

        fig = go.Figure(data)
        fig.update_layout(barmode='stack')

#        fig = px.bar(
#            df_grindage, 
#            x='Duration',
#            y='Title',
#            color='Stage',
#            title='Repertoire Progress',
#        )

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
        
    
        