"""Contains the html layout for the Reinforcement Learning tab"""

from datetime import datetime as dt

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

securities = [
    "AMZN",
    "NFLX",
    "NVDA",
    "AMD",
    "JPM",
    "CFG",
    "GS",
    "MS",
    "USB",
    "BAC",
    "GLD",
    "QQQ",
]
securities = [{"label": i, "value": i} for i in securities]


def load_html() -> html.Div:
    return html.Div(
        [
            html.Div(
                [
                    dcc.Graph(
                        id="rl-graph",
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
                            html.Label("Select Security", style=styling),
                            dcc.Dropdown(
                                options=securities,
                                value=None,
                                multi=False,
                                clearable=False,
                                id="rl-stock-picker",
                                style={"textAlign": "center", "align": "center"},
                            ),
                        ]
                    ),
                    html.Div(
                        [
                            html.Label("Training Date Range", style=styling),
                            dcc.DatePickerRange(
                                id="train-rl-date-ranger",
                                min_date_allowed=dt(2008, 1, 1),
                                max_date_allowed=dt.now().date(),
                                start_date=dt(
                                    dt.now().year - 2, dt.now().month, dt.now().day - 1
                                ).date(),
                                end_date=dt(
                                    dt.now().year - 1, dt.now().month, dt.now().day - 1
                                ).date(),
                                calendar_orientation="horizontal",
                            ),
                        ],
                        style={"align": "center", "textAlign": "center"},
                    ),
                    html.Div(
                        [
                            html.Label("Testing Date Range", style=styling),
                            dcc.DatePickerRange(
                                id="test-rl-date-ranger",
                                min_date_allowed=dt(2008, 1, 1),
                                max_date_allowed=dt.now().date(),
                                start_date=dt(
                                    dt.now().year - 1, dt.now().month, dt.now().day - 1
                                ).date(),
                                end_date=dt(
                                    dt.now().year, dt.now().month, dt.now().day - 1
                                ).date(),
                                calendar_orientation="horizontal",
                            ),
                        ],
                        style={"align": "center", "textAlign": "center"},
                    ),
                    html.Button("Execute Model", id="rl-button"),
                    html.Label("Strategy Returns", style=styling),
                    DataTable(
                        columns=[
                            {"id": i, "name": i} for i in ["Q Learner", "Buy and Hold"]
                        ],  # initialise the rows
                        id="rl-datatable",
                        style_cell=styling3,
                    ),
                ],
                style={
                    "textAlign": "center",
                    "align": "center",
                    "float": "left",
                    "width": "40%",
                },
            ),
            html.Div(
                [
                    dcc.Markdown(
                        """

#### Instructions
- Select a Security Ticker from the dropdown menu
- Select a training date range and testing date range
- Click the button "Execute Model".
- Model results will display in ~5 seconds.

#### Reinforcement Learning - Q Learner:
This model is a 3-action dyna enchanced Q Learner with the following discretized attributes.
1. Bollinger Bands Signal: Long, Exit, Short
2. Relative Strength Index Signal: Long, Exit, Short
3. On Balance Value Signal: Long, Exit, Short
4. Moving Average Convergence Divergence Signal: Long, Short

The model is semi-temporal as it also takes into account the day of the week.
As such, the Q-Learner state space is: 3x3x3x3x2x5 = **810 spaces**
 (#actions x #Bol Band signals x #RSI signals x #OBV signals x #MACD signals x #Weekdays).

#### Results:
By some measure of luck, the model seems to do extremely well with financial stocks.  Examples include:
- JP Morgan Chase (JPM)
- Citizens Bank (CFG)
- Goldman Sachs (GS)
- Morgan Stanley (MS)
- US Bank Corp (USB)
- Bank of America (BAC)

....And the model completely falls apart with other stocks:
- Amazon (AMZN)
- NVDA (NVDA)
- Netflix (NFLX)
- AMD (AMD)"""
                    )
                ],
                style={
                    "textAlign": "left",
                    "align": "center",
                    "float": "right",
                    "width": "100%",
                },
            ),
        ]
    )
