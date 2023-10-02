"""Contains the intial app layout and the main function for running the Dash app"""

from dash import Dash, dcc, html

from asset_allocator import callbacks as asset_allocator_callbacks
from asset_allocator import frontend as asset_allocator_frontend

from rlmodel import frontend as rl_frontend

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


app = Dash(__name__, external_stylesheets=external_stylesheets)

server = app.server

asset_allocator_callbacks.get_callbacks(app)

app.layout = html.Div(
    [
        html.Div(
            [html.H2("Technical Analysis Dashboard, Christian Rivera")],
            style={
                "color": "grey",
                "textAlign": "center",
                "font-family": "Georgia",
            },
        ),
        html.Div(id="hidden-graph-data", style={"display": "none"}),
        html.Div(id="hidden-table-data", style={"display": "none"}),
        html.Div(id="hidden-rl-data", style={"display": "none"}),
        dcc.Tabs(
            id="tabs",
            children=[
                dcc.Tab(
                    label="Asset Allocation Optimizer",
                    children=[asset_allocator_frontend.load_html()],
                ),
                # dcc.Tab(
                #    label="Dynamic Bollinger Bands & OHLC Graphs",
                #    children=[
                #        # tabCode.getTab2()
                #    ],
                # ),
                dcc.Tab(
                    label="Reinforcement Learning Model Example",
                    children=[rl_frontend.load_html()],
                ),
                dcc.Tab(
                    label="About",
                    children=[
                        dcc.Markdown(
                            """## To Whom it May Concern

This is a sample Dash Python application showcasing some of my skills.  Dash is a web framework by Plotly and is like Streamlit in its use.

This app is meant to show the following skills:
- **Quantitative Analyst**
  - Expert knowledge of quantitative python packages like `pandas` and `numpy`
  - Portfolio Construction knowledge
  - Ability to implement Machine Learning and Reinforcemment Learning trading strategies into a deliverable product
- **Software Development**
  - Knowledge and implementation of cloud computing technology (this is launched on Google Cloud but I also have AWS Solutions Architect certification and have worked in AWS professionally)
  - Ability to write clean, maintainable code following best practices (formatting, static typing, testing)

[The Gitub repo for this code can be found here](https://github.com/crivera2013/invest-dash)

[A link to some of my other work can be found here](https://crivera2013.github.io/)

[And my LinkedIn can be found here](https://Linkedin.com/in/chrisian-rivera-vanguard)"""
                        )
                    ],
                ),
            ],
        ),
    ]
)

# Only for running on development mode
if __name__ == "__main__":
    app.run(debug=True)
