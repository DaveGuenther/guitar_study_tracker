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

        def make_stacked_bar_traces(dimension_a, dimension_b, field_3, dimension_a_unique_sort_order=None, dimension_b_unique_sort_order=None):
            """
            dimension_a, dimension_b  (str): column name of a dimension in the incoming dataframe.  These will be the rows and columns of the matrix that is built.
            field_3 (str): column name of a measure or dimension in the dataframe who's value will be isolated in the intersection of dimension_a and dimension_b.
            dimension_a_unique_sort_order (list): This is a list of the unique values of dimension_a sorted in any manner the usert wants. If omitted, it will use the data source order of unique values of dimension_a. 

            Ex df_summary:
            +--------+--------+----------+
            | cat_a  | cat_b  |  measure |
            +--------+--------+----------+
            | Red    | Circle | 10       |
            | Red    | Square | 5        |
            | Green  | Diamond| 6        |
            | Green  | Square | 11       |
            | Purple | Circle | 3        |
            | Purple | Diamond| 2        |
            | Purple | Square | 6        |
            | Blue   | Circle | 8        |
            | Blue   | Diamond| 9        |
            +--------+--------+----------+
            df = pd.DataFrame({
                'cat_a':['Red','Red','Green','Green','Purple','Purple','Purple','Blue','Blue'],
                'cat_b':['Circle','Square','Diamond','Square','Circle','Diamond','Square','Circle','Diamond'],
                'measure': [10,5,6,11,3,2,6,8,9]})


            trace_dict = make_stacked_bar_traces(df['cat_a'], df['cat_b'],df['measure'])
            returns:
            {
                'dim_a_unique':['Red','Green','Purple','Blue'],
                'dim_b_unique':['Circle','Square','Diamond'],
                'field_3_values':[
                            [10.0, 0.0, 3.0, 8.0],  #Circle
                            [5.0, 11.0, 6.0, 0.0],  #Square
                            [0.0, 6.0, 2.0, 9.0]    #Diamond
                        ]
            }

            Use this to build traces for plotly bars:
            
            from plotly import go
            data = [go.Bar(name=color, x = trace_dict['dim_a_unique'], y=duration) for color,duration in zip(trace_dict['dim_b_unique'],trace_dict['field_3_values'])]
            fig = go.Figure(data)
            fig.update_layout(barmode='stack')

            """
            if not dimension_a_unique_sort_order:
                dimension_a_unique_sort_order = list(dimension_a.unique())
            if not dimension_b_unique_sort_order:
                dimension_b_unique_sort_order = list(dimension_b.unique())

            df_in = pd.DataFrame({'dim_a':dimension_a, 'dim_b':dimension_b, 'field_3':field_3})
            
            df_in['dim_a'] = pd.Categorical(df_in['dim_a'], categories=dimension_a_unique_sort_order, ordered=True)
            df_in['dim_b'] = pd.Categorical(df_in['dim_b'], categories=dimension_b_unique_sort_order, ordered=True)
            df_in = df_in.sort_values(['dim_a','dim_b'])
            df_in_pivot = df_in.pivot(columns=['dim_a'],index=['dim_b'])
            dim_a_uniques = list(df_in['dim_a'].unique())
            dim_b_uniques = list(df_in['dim_b'].unique())
            dim_b_vals = list(df_in_pivot.index)
            dim_c_vals=[]
            for dim_b in dim_b_vals:
                dim_c_vals.append(list(df_in_pivot.loc[dim_b]['field_3'].fillna(0)))
            return {'dim_a_unique':dim_a_uniques, 'dim_b_unique':dim_b_uniques,'field_3_values':dim_c_vals}


        stage_order = ['Learning Notes','Achieving Tempo','Phrasing','Maintenance']
        title_order = list(df_grindage.groupby('Title')['Duration'].sum().sort_values(ascending=False).index)
        trace_dict = make_stacked_bar_traces(df_grindage['Title'], df_grindage['Stage'],df_grindage['Duration'], dimension_a_unique_sort_order=title_order, dimension_b_unique_sort_order=stage_order)

        data = [go.Bar(name=color, x = trace_dict['dim_a_unique'], y=duration) for color,duration in zip(trace_dict['dim_b_unique'],trace_dict['field_3_values'])]

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
        
    
        