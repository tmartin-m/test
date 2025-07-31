# Imports
from shiny.express import input
from shiny import reactive, App, ui, render
from shinywidgets import output_widget, render_widget, render_plotly
import pandas as pd
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt

# Load data 
iris = sns.load_dataset("iris")

# UI Layout
app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.sidebar(
            ui.h2("Sidebar"),
            ui.input_selectize(
                "selected_attribute",
                "Choose a column:",
                ["sepal_length", "sepal_width", "petal_length", "petal_width", "species"]
            ),
            ui.input_numeric(
                "plotly_bin_count",
                "Plotly Bin Count",
                10
            ),
            ui.input_slider(
                "seaborn_bin_count",
                "Seaborn Bin Count",
                1,
                100,
                5
            ),
            ui.input_checkbox_group(
                "selected_species_list",
                "Selected Bin List",
                ["Setosa", "Versicolor", "Virginica"],
                selected=["Setosa", "Versicolor", "Virginica"],
                inline=True
            ),
            ui.hr(),
            ui.a(
                "GitHub",
                href="",
                target="_blank"
            )
        ),
        ui.layout_columns(
            ui.output_data_frame("penguin_data_table"),
            ui.output_data_frame("penguin_data_grid")
        ),
        ui.layout_columns(
            output_widget("plotly_histogram"),
            ui.output_plot("seaborn_hist"),  
        ),
        ui.card(
            ui.card_header("Plotly Scatterplot: Species"),
            output_widget("plotly_scatterplot"),
            full_screen=True
        )
    )
)

# Define Server
def server(input, output, session):

    @output
    @render.data_frame
    def penguin_data_table():
        return render.DataTable(penguins_df, filters=True)

    @output
    @render.data_frame
    def penguin_data_grid():
        return render.DataGrid(penguins_df, filters=True)

    @output
    @render_widget
    def plotly_histogram():
        fig = px.histogram(
            penguins_df,
            x=input.selected_attribute(),
            color="species",
            barmode="overlay",
            nbins=input.plotly_bin_count(),
            title=f"Histogram of {input.selected_attribute()} by Species"
        )
        return fig

    @output
    @render.plot
    def seaborn_hist():
        plt.figure(figsize=(8, 4))
        df = penguins_df.dropna(subset=["body_mass_g", "species"])
        sns.histplot(
            data=df, 
            x="body_mass_g", 
            hue="species", 
            multiple="layer", 
            bins=input.seaborn_bin_count()
        )
        plt.title("Seaborn Histogram of Body Mass by Species")
        plt.xlabel("Body Mass (g)")
        plt.ylabel("Count")
        return plt.gcf()
        
    @output
    @render_widget
    def plotly_scatterplot():
        fig = px.scatter(
            penguins_df,
            x="flipper_length_mm",
            y="body_mass_g",
            color="species",
            title="Scatterplot: Flipper Length vs Body Mass"
        )
        return fig

# Launch the app
app = App(app_ui, server)
