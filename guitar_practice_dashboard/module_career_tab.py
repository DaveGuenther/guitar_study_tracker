# Core
import math
from datetime import date
import pandas as pd

# Utility
import logger

# Web/Visual frameworks
from shiny import ui, module, reactive, render
import plotly.graph_objects as go
import plotly.express as px
from shinywidgets import output_widget, render_widget, render_plotly

# App Specific Code
import global_data
globals = global_data.GlobalData()

Logger = logger.FunctionLogger


df_sessions = globals.get_df_sessions()
df_grindage = globals.get_df_arrangement_grindage()
df_arrangement_grindage = df_grindage[df_grindage['Song Type']=='Song']
df_exercise_grindage = df_sessions[df_sessions['Song Type']=='Exercise']


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
        ui.row(
            ui.card(
                ui.output_text(id="avg_practice_time").add_class('ban-text'),
                ui.h5("Avg. Practice Time/Day"),
            ).add_class('ban-card'),

            ui.card(
                ui.output_text(id='longest_consecutive_streak').add_class('ban-text'),
                ui.h5("Longest Practice Streak"),

            ).add_class('ban-card'),                        
            ui.card(
                ui.output_text(id='longest_session').add_class('ban-text'),
                ui.h5("Longest Session"),

            ).add_class('ban-card'),
            ui.card(
                ui.output_text(id='total_practice_time').add_class('ban-text'),
                ui.h5("Total Practice Time"),

            ).add_class('ban-card'),
            ui.card(
                ui.output_text('career_length_yrs').add_class('ban-text'),
                ui.h5("Career Length"),

            ).add_class('ban-card'),                                                     
        ).add_class('ban-row'),
        ui.card(
            ui.div("Time Spent Studying Songs").add_class('chart-title'),
            ui.output_ui(id='arrangement_grind_legend').add_class('legend-font'),
            output_widget(id='arrangement_grindage_chart'),
        ).add_class('dashboard-card'),     
        ui.card(
            ui.div("Time Spent Studying Exercises").add_class('chart-title'),
            output_widget(id='exercise_grindage_chart'),
        ).add_class('dashboard-card'),   
        ui.div(class_='flex-blank'),
            ui.h6(
                ui.span("").add_class('flex-blank'),
                #ui.div(ui.HTML(video_link)),
                ui.tags.a("Dave Guenther",href="https://www.linkedin.com/in/dave-guenther-915a8425a",target='_blank'),
                ", 2024",
                ui.span("").add_style("width:5px; display:inline;"),  
                "|",
                ui.span("").add_style("width:5px; display:inline;"),  
                "Source Code:",
                ui.tags.a("GitHub",href="https://github.com/DaveGuenther/guitar_study_tracker",target='_blank'),
                ui.span("").add_style("width:5px; display:inline;"),
                "|",
                ui.span("").add_style("width:5px; display:inline;"),  
                "Data Source:",
                ui.tags.a("Supabase",href="https://supabase.com/",target='_blank'),
            ).add_class('flex-horizontal').add_style('flex-wrap:wrap;'), 
    )
    

    return ret_val

@module.server
def career_server(input, output, session):
    Logger(session.ns)

    @render.text
    def longest_session():
        flt_max = (df_sessions.groupby('Session Date')['Duration'].sum()).max()
        minutes = math.floor(flt_max)
        return f"{minutes} Mins"

    @render.text
    def avg_practice_time():
        flt_avg = (df_sessions.groupby('Session Date')['Duration'].sum()).mean()
        minutes=math.floor(flt_avg)
        return f"{minutes} Mins"
    
    @render.text
    def total_practice_time():
        total_minutes = (df_sessions.groupby('Session Date')['Duration'].sum()).sum()
        total_hrs = math.floor(total_minutes/60) 
        return f"{total_hrs} Hrs"
    
    @render.text
    def longest_consecutive_streak():
        ser_dates = df_sessions['session_date'].unique()
        df=pd.DataFrame({'Date':ser_dates})
        df = df.sort_values('Date')
        df['date_diff'] = df['Date'].diff().dt.days
        df['streak_group'] = (df['date_diff'] != 1).cumsum()

        streak_counts = df.groupby('streak_group').size()
        longest_streak = streak_counts.max()
        longest_streak_group_num = streak_counts[streak_counts==longest_streak].index[0]
        streak_start_date = df[df['streak_group']==longest_streak_group_num]['Date'].min()
        streak_end_date = df[df['streak_group']==longest_streak_group_num]['Date'].max()
        return f"{longest_streak} Days"

    @render.text
    def career_length_yrs():
        start_date = df_sessions['session_date'].min()
        end_date = df_sessions['session_date'].max()
        career_length = end_date - start_date
        career_length_days = career_length.days
        return f"{math.floor((career_length_days/365.25)*10)/10} Yrs"
        


    @render_widget
    def arrangement_grindage_chart():
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
        title_order = list(df_arrangement_grindage.groupby('Title')['Duration'].sum().sort_values(ascending=True).index)
        trace_dict = make_stacked_bar_traces(df_arrangement_grindage['Title'], df_arrangement_grindage['Stage'],round((df_arrangement_grindage['Duration']/60)*10)/10, dimension_a_unique_sort_order=title_order, dimension_b_unique_sort_order=stage_order)

        category_colors={'Learning Notes':['#801100',4],
                         'Achieving Tempo':['#d73502',3],
                         'Phrasing':['#ff7500',2],
                         'Maintenance':['#FAC000',1]}


        data = [go.Bar(name=stage, 
                       y = trace_dict['dim_a_unique'], 
                       x=duration, orientation='h', 
                       legendrank=category_colors[stage][1],
                       customdata=[stage for i in range(len(trace_dict['dim_a_unique']))],
                       marker=dict(
                           {
                               'color':category_colors[stage][0], # assign custom colors to each trace
                               'cornerradius':30, # make tip of bar curved
                               'line_color':'rgba(0, 0, 0, 0)', # remove the border around each bar segment
                            })) for stage,duration in zip(trace_dict['dim_b_unique'],trace_dict['field_3_values'])]

        fig = go.Figure(data)
        fig.update_layout(barmode='stack')

        fig.update_traces(
            hovertemplate='Song: %{y}<br>Stage: %{customdata}<br>Practice Time (Hours): %{x}<extra></extra>',
        )

        fig.update_layout(
            showlegend=False,

            # Main plot styling
            font_family='garamond',            
            font_color='#Ff9b15',
            paper_bgcolor='rgba(0, 0, 0, 0)', # background for all area that is not the plot marks themselves
            xaxis_tickfont=dict(size=14), # y label styling
            yaxis_tickfont=dict(size=14), # x label styling
            xaxis_gridcolor='#8c550c', # Vertical Tick Lines colored darker brown
            xaxis_zerolinecolor='#8c550c', # X- Zero vertical tick line colord darker brown

            plot_bgcolor='rgba(0, 0, 0, 0)', # background for the actual plot area (plot marks themselves)
            height=20+(len(trace_dict['dim_a_unique'])*50),

            # Tooltip Styling
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Garamond",
                bordercolor="black",
                align="left"
            ),

        )

        fig.update_xaxes(
            title_text="Hours",
        )
        figWidget = go.FigureWidget(fig)
        return figWidget

    def custom_categorical_legend(legend_id, categories={'One':'red','Two':'Green','Three':'blue'},size=20, border_radius=5, border='1px solid black'):
        """
        
        """
        legend_id = str(legend_id)
        styles = """
            <style>
                .legend"""+legend_id+""" {
                    display: flex;
                    flex-wrap: wrap;
                    align-items: center;
                }

                .legend-item"""+legend_id+""" {
                    display: flex;
                    align-items: center;
                    margin-right: 10px;
                    
                }

                .legend-color"""+legend_id+""" {
                    width: """+str(size)+"""px;
                    height: """+str(size)+"""px;
                    border: """+border+""";
                    margin-right: 5px;
                    border-radius: """+str(border_radius)+"""px;
                }
            </style>
            """
        legend = """
            <div class="legend"""+legend_id+"""">
            """
        for category, color in zip(categories.keys(), categories.values()):
            legend_item="""
                <div class="legend-item"""+legend_id+"""">
                    <div class="legend-color"""+legend_id+"""" style="background-color: """+color+""";"></div>
                    <span>"""+category+"""</span>
                </div>
                """
            legend+=legend_item
        legend+="""
            </div>
            """
        return styles+legend

    @render.text
    def arrangement_grind_legend():
        category_colors={'Learning Notes':'#801100',
                         'Achieving Tempo':'#d73502',
                         'Phrasing':'#ff7500',
                         'Maintenance':'#FAC000'}
        legend_id = str(globals.get_legend_id())
        legend = custom_categorical_legend(legend_id, category_colors)
        ret_val = legend
        return ret_val
    
    @render_widget
    def exercise_grindage_chart():

        ser_ex_bar_prep = df_exercise_grindage.groupby('Song')['Duration'].sum().sort_values()
        titles=list(ser_ex_bar_prep.index)
        durations = list(round((ser_ex_bar_prep/60)*10)/10)
        round((df_arrangement_grindage['Duration']/60)*10)/10

        fig = go.Figure(go.Bar(
            x=durations, 
            y=titles, 
            orientation='h',
            marker=dict(cornerradius=30),         
            ))      

        fig.update_traces(
            marker_color="#03A9F4",
            hovertemplate='Exercise: %{y}<br>Practice Time (Hours): %{x}<extra></extra>',
            #width=.5,
        )
        fig.update_layout(
            dragmode=False,
            modebar=dict(remove=['zoom2d','pad2d','select2d','lasso2d','zoomIn2d','zoomOut2d','autoScale2d']),
            
            # Main plot styling
            font_family='garamond',
            font_color='#Ff9b15',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            
            # Axis Label Size
            yaxis_tickfont=dict(size=14),
            xaxis_gridcolor='#8c550c', # Vertical Tick Lines colored darker brown
            xaxis_zerolinecolor='#8c550c', # X- Zero vertical tick line colord darker brown

            plot_bgcolor="rgba(0, 0, 0, 0)",
            height=20+(len(titles)*50),

            # Tooltip Styling
            hoverlabel=dict(
                bgcolor="white",
                font_size=14,
                font_family="Garamond",
                bordercolor="black",
                align="left"
            ),
        )
        fig.update_xaxes(title_text='Hours')
        fig.layout.xaxis.fixedrange = True
        fig.layout.yaxis.fixedrange = True

        figWidget = go.FigureWidget(fig)
        return figWidget  