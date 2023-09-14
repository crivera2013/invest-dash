"""Contains the html layout for the portfolio optimization asset allocator tab"""

import pandas as pd
from dash import dcc, html
from dash.dash_table import DataTable

styling = {  # 'textAlign':'center',
    "font-family": "Georgia",
    "font-size": "18px",
    "padding": "10px",
    "text-align": "center",
}


styling2 = {  # 'textAlign':'center',
    "font-family": "Georgia",
    "font-size": "18px",
    "padding": "10px",
    "text-align": "left",
}

styling3 = {  # 'textAlign':'center',
    "font-family": "Georgia",
    "font-size": "12px",
    "padding": "4px",
    "text-align": "center",
}

securities = pd.read_csv("asset_allocator/ticker_universe.csv")
securities.columns = ["label"]
securities["value"] = securities["label"]
securities = securities.to_dict("records")
securities.append({"label": "GLD", "value": "GLD"})


def load_html() -> html.Div:
    """Returns the html layout for the portfolio optimization asset allocator tab"""
    return html.Div(
        [
            html.Div(
                [
                    dcc.Graph(
                        id="the-graph",
                        config={
                            "displayModeBar": False,
                            "scrollZoom": True,
                        },
                    ),
                ],
                style={
                    "textAlign": "center",
                    "align": "center",
                    "float": "left",
                    "width": "60%",
                },
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Select Securities", style=styling),
                            dcc.Dropdown(
                                options=securities,
                                value=["GOOG", "AAPL", "F"],
                                multi=True,
                                clearable=False,
                                id="stock-picker",
                                style={"textAlign": "center", "align": "center"},
                            ),
                        ]
                    ),
                    html.Label("Date Range", style=styling),
                    dcc.RadioItems(
                        options=[
                            {"label": "6 Months", "value": "6m"},
                            {"label": "YTD", "value": "ytd"},
                            {"label": "1 Year", "value": "1y"},
                            {"label": "2 Year", "value": "2y"},
                        ],
                        labelStyle={
                            "width": "25%",
                            "display": "block",
                            "font-family": "Georgia",
                            "font-size": "12px",
                            "float": "left",
                            "align": "left",
                            "textAlign": "left",
                        },
                        style={"align": "left", "textAlign": "center"},
                        value="1y",
                        id="date-ranger",
                    ),
                    html.Label("Current Portfolio", style=styling),
                    DataTable(
                        id="datatable",
                        style_cell=styling3,
                    ),
                    html.Div(
                        [
                            html.Label("Metrics", style=styling),
                            DataTable(
                                columns=[
                                    {"id": i, "name": i}
                                    for i in [
                                        "Sharpe Ratio",
                                        "Absolute Return",
                                        "Minimum Volatility",
                                    ]
                                ],  # initialise the rows
                                id="infotable",
                                style_cell=styling3,
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Label("Local Optimized Value", style=styling),
                            dcc.RadioItems(
                                options=[
                                    {"label": "Sharpe Ratio", "value": "sr"},
                                    {"label": "Absolute Return", "value": "ar"},
                                    {"label": "Minimum Volatility", "value": "mv"},
                                ],
                                labelStyle={
                                    "display": "block",
                                    "font-family": "Georgia",
                                    "font-size": "12px",
                                },
                                value="sr",
                                id="optimizer",
                                style={"align": "left"},
                            ),
                            html.Label("Benchmarking Index", style=styling),
                            dcc.RadioItems(
                                options=[
                                    {"label": "S&P 500", "value": "SPY"},
                                    {"label": "Russell 2000", "value": "IWM"},
                                    {
                                        "label": "Vanguard FTSE All World Ex US",
                                        "value": "VEU",
                                    },
                                ],
                                value="SPY",
                                labelStyle={
                                    "display": "block",
                                    "font-family": "Georgia",
                                    "font-size": "12px",
                                },
                                id="benchmarker",
                                style={"align": "left"},
                            ),
                        ],
                        style={"columnCount": 2},
                    ),
                ],
                style={
                    "textAlign": "center",
                    "align": "center",
                    "float": "left",
                    "width": "40%",
                },
            ),
        ]
    )
