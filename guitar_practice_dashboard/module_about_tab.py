# Core
from shiny import ui, module, render
from datetime import date
import pandas as pd
import mdtex2html
import latex2mathml.converter

# Utility
import logger

# App Specific Code
import global_data
globals = global_data.GlobalData()

Logger = logger.FunctionLogger

@module.ui
def about_ui():
    ret_val = ui.nav_panel(
        "About",
        ui.page_navbar(
            ui.nav_panel(
                'About This Dashboard',
                ui.markdown("""
                    I built this hobby project to track my progress learning the classical guitar and to explore the new Shiny for Python framework.  This section of the dashboard documents the design and development process including requirements, wireframes, high level design, data engineering, data integration, and visual development.  I’ll also pepper in challenges I ran into and solutions/lessons learned for future dashboard projects using Shiny for Python.  If this sounds like fun, please keep reading!

                    I have included the full source for this application via my github repo (link at bottom) in case you see something useful in here that you’d like to carry into your own project.  While this application by default reads from a live PostgreSQL database, I’ve included a local SQLite version of the data in the repository.  Simply cloning the repository and running the dashboard should have it automatically read the on-disk database.  More on this is in the Repository Structure section.

                    I pulled out some parts of this dashboard that were reusable and started tracking minimal reproducible examples in a separate git repository: [Python-Shiny-Examples](https://github.com/DaveGuenther/Python-Shiny-Examples).  I’ll refer to some specific examples in this writeup.
                    """
                ),
                
            ),
            id='about_nav_bar',     
            title="",
        ),
        ui.HTML("<br>"+
            latex2mathml.converter.convert("""h(n) = -\sum_{i=0}^{n}(max(kt_{i},d))+100""")+
            "<br>where:<br>"+
            latex2mathml.converter.convert("""h(n)""")+" = string health at day "+latex2mathml.converter.convert("""n""")+"<br>"+
            latex2mathml.converter.convert("""t_{i}""")+" = time played on day "+latex2mathml.converter.convert("""i""")+" (minutes)<br>"+
            latex2mathml.converter.convert("""k""")+" = time-based coefficient "+latex2mathml.converter.convert("""(\\frac{1}{60}""")+" hrs"+latex2mathml.converter.convert(""")""")+"<br>"+
            latex2mathml.converter.convert("""d""")+" = day-based coefficient "+latex2mathml.converter.convert("""(\\frac{1}{112}""")+" days"+latex2mathml.converter.convert(""")""")+"<br>"
        ),


    ),
    return ret_val


@module.server
def about_server(input, output, session):
    Logger(session.ns)
    
    @render.text
    def mdIntro():
        return (
            """
            I built this hobby project to track my progress learning the classical guitar and to explore the new Shiny for Python framework.  This section of the dashboard documents the design and development process including requirements, wireframes, high level design, data engineering, data integration, and visual development.  I’ll also pepper in challenges I ran into and solutions/lessons learned for future dashboard projects using Shiny for Python.  If this sounds like fun, please keep reading!

            I have included the full source for this application via my github repo (link at bottom) in case you see something useful in here that you’d like to carry into your own project.  While this application by default reads from a live PostgreSQL database, I’ve included a local SQLite version of the data in the repository.  Simply cloning the repository and running the dashboard should have it automatically read the on-disk database.  More on this is in the Repository Structure section.

            I pulled out some parts of this dashboard that were reusable and started tracking minimal reproducible examples in a separate git repository: [Python-Shiny-Examples](https://github.com/DaveGuenther/Python-Shiny-Examples).  I’ll refer to some specific examples in this writeup.
            """)
