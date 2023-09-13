from dash import Dash, dcc, html
from asset_allocator import frontend as asset_allocator_frontend
from asset_allocator import callbacks as asset_allocator_callbacks

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]


app = Dash(__name__, external_stylesheets=external_stylesheets)

asset_allocator_callbacks.get_callbacks(app)

app.layout = html.Div(
    [
        html.Div(
            [html.H2("Technical Analysis Dashboard, Christian Rivera")],
            style={"color": "grey", "textAlign": "center", "font-family": "Georgia"},
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
                dcc.Tab(
                    label="Dynamic Bollinger Bands & OHLC Graphs",
                    children=[
                        # tabCode.getTab2()
                    ],
                ),
                dcc.Tab(
                    label="IEX Real-Time Data Feed ",
                    children=[
                        # tabCode.getTab3()
                    ],
                ),
                dcc.Tab(
                    label="Reinforcement Learning",
                    children=[
                        # tabCode.getTab4()
                    ],
                ),
            ],
        ),
    ]
)

#############################################


#############################################
if __name__ == "__main__":
    app.run(debug=True)
