import plotly.express as px
from shiny import App, ui, render, reactive
from shinywidgets import output_widget, render_widget
import seaborn as sns
import matplotlib.pyplot as plt
from palmerpenguins import load_penguins

penguins_df = load_penguins()

# Define UI
app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.sidebar(
            ui.h2("Sidebar"),
            ui.input_selectize(
                "selected_attribute",
                "Choose a column:",
                ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
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
                "Selected Species List",
                ["Adelie", "Gentoo", "Chinstrap"],
                selected=["Adelie", "Gentoo", "Chinstrap"],
                inline=True
            ),
            ui.hr(),
            ui.a(
                "GitHub",
                href="https://github.com/tmartin-m/cintel-02-data/blob/main/app.py",
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

    # --------------------------------------------------------
    # Reactive calculation to filter the data
    # --------------------------------------------------------

    @reactive.calc
    def filtered_data():
        # Drop rows with NA in the selected attribute
        df = penguins_df.dropna(subset=[input.selected_attribute()])
        # Filter by species selected
        df = df[df["species"].isin(input.selected_species_list())]
        return df

    @output
    @render.data_frame
    def penguin_data_table():
        return render.DataTable(filtered_data())

    @output
    @render.data_frame
    def penguin_data_grid():
        return render.DataGrid(filtered_data())

    @output
    @render_widget
    def plotly_histogram():
        fig = px.histogram(
            data_frame=filtered_data(),
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
        sns.histplot(
            data=filtered_data(),
            x=input.selected_attribute(),
            hue="species",
            multiple="layer",
            bins=input.seaborn_bin_count()
        )
        plt.title(f"Seaborn Histogram of {input.selected_attribute()} by Species")
        plt.xlabel(input.selected_attribute())
        plt.ylabel("Count")
        return plt.gcf()

    @output
    @render_widget
    def plotly_scatterplot():
        fig = px.scatter(
            penguins_df.dropna(subset=["flipper_length_mm", "body_mass_g"]),
            x="flipper_length_mm",
            y="body_mass_g",
            color="species",
            title="Scatterplot: Flipper Length vs Body Mass"
        )
        return fig

# Launch the app
app = App(app_ui, server)
