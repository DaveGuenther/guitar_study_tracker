from shiny import ui
from shinywidgets import output_widget
from datetime import datetime, date
import pandas

def timestamp_to_date(this_timestamp: pandas._libs.tslibs.timestamps._Timestamp):
    return date(this_timestamp.year, this_timestamp.month, this_timestamp.day)



def tab_session(df_365):

    def sessions_filter_shelf(df_365):
        songs = df_365[df_365['Song'].notna()]['Song'].unique()
        ret_val = ui.div(
            ui.h3("Filters:"),
            ui.input_checkbox_group(
                "song_title",
                "Song Title",
                choices={key:value for key,value in zip(songs, songs)},
                selected=[key for key in songs],
            ),
            #ui.input_select(id='song_title',label="Song Title",choices=list(df_sessions['Song'].unique()),selected=list(df_sessions['Song'].unique()),multiple=True)
        )
        return ret_val

    ret_val = ui.nav_panel("Practice Sessions", 
        ui.page_sidebar(
            ui.sidebar(
                sessions_filter_shelf(df_365),
                open="closed",
            ),
            ui.card(
                ui.div(
                    output_widget(id='waffle_chart'),
                    ui.img(src='guitar-head-stock.png', height="240px"),
                    id='guitar-neck-container',
                ).add_style('width:1750px; overflow-x: auto; display: flex; margin:0px; padding:0px;'),
                ui.div("* Indicates that a video recording was made that day.").add_style("text-align:right;"),
                class_="dashboard-card",
            ),
        
            ui.row(

                ui.column(6,
                    ui.div(
                        ui.card(
                            ui.h3("Practice Session Notes (Past Week)"),#.add_style("color:#Ff9b15;"),
                            output_widget(id='last_week_bar_chart').add_style('height:200px; overflow-y: auto; display: flex;'),
                            ui.div(ui.output_data_frame(id="sessionNotesTable").add_class('dashboard-table')).add_style('max-height:200px; overflow-y: clip; display: flex;'),
                            ui.div("",class_='blank-fill-container'),
                            class_="dashboard-card",
                        ),
                    ),
                ).add_style("padding-right:6px;"),

                ui.column(6,
                    
                    ui.card(
                        ui.div(
                            ui.h3("Time Spent Practicing Songs (Past Year)"),
                            output_widget(id='last_year_bar_chart'),
                            ui.div(class_='flex-blank'),
                        ).add_class("flex-vertical",)
                    ).add_class("dashboard-card").add_style('overflow-y: auto; display: flex;'),
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
                ).add_class("flex-vertical").add_style("padding-left:6px;"),
            ).add_style("margin-top: 10px;"),    
                
            

        ),
    )
    return ret_val


def tab_career(df_sessions):

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
        