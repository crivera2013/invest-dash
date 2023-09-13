from dash import Input, Output, State
from plotly.graph_objs import Layout, Scatter
import pandas as pd
import json
import requests


def get_callbacks(app):
    @app.callback(
        Output(component_id="the-graph", component_property="figure"),
        [Input("hidden-table-data", "children")],
    )
    def line_graph(values):
        values = json.loads(values)

        portfolio = pd.DataFrame(values["portfolio"])
        portfolio["Date"] = pd.to_datetime(values["dates"], format="%Y-%m-%d")
        portfolio.set_index("Date", inplace=True)

        traces = []

        traces.append(
            Scatter(
                x=portfolio.index,
                y=portfolio.Portfolio,
                # text=df_by_continent['country'],
                opacity=0.7,
                mode="lines",
                line=dict(
                    color="light Green",
                ),
                name="Portfolio",
            )
        )

        traces.append(
            Scatter(
                x=portfolio.index,
                y=portfolio[values["benchmark"]],
                # text=df_by_continent['country'],
                opacity=0.7,
                mode="lines",
                line=dict(
                    color="light Blue",
                ),
                name="Benchmark: " + values["benchmark"],
            )
        )

        layout = Layout(
            title="Portfolio vs Benchmark Performance",
            yaxis={"title": "Normalized Price ($)"},
            hovermode="closest",
            legend=dict(x=0, y=1),
        )

        config = {"scrollZoom": True, "displayModeBar": False, "editable": False}

        results = {"data": traces, "layout": layout, "config": config}

        return results

    @app.callback(Output("datatable", "data"), [Input("hidden-table-data", "children")])
    def tableTime(values):
        values = json.loads(values)
        stocks = values["stocks"]
        allocations = values["allocations"]

        allocations = [str(round(i * 100, 2)) + "%" for i in allocations]

        record = [dict(zip(stocks, allocations))]
        return record

    @app.callback(
        Output(component_id="hidden-graph-data", component_property="children"),
        [
            Input(component_id="date-ranger", component_property="value"),
            Input(component_id="stock-picker", component_property="value"),
        ],
        [
            State(component_id="benchmarker", component_property="value"),
            State(component_id="optimizer", component_property="value"),
        ],
    )
    def get_the_data(daterange, stocks, benchmark, optimizer):
        initial_port, dates = getPortfolio(daterange, stocks)

        initial_port = initial_port.to_dict("records")

        result = dict(initial_port=initial_port, dates=dates, stocks=stocks)

        return json.dumps(result)


def getPortfolio(daterange, symbols, df=None):
    symbols = symbols + ["SPY", "IWM", "VEU"]
    params = {
        "symbols": ",".join(symbols),
        "types": "chart",
        "range": daterange,
        "filter": "close,date",
    }
    url = "https://api.iextrading.com/1.0/stock/market/batch"
    a = requests.get(url, params=params).json()
    for i in a.keys():
        b = pd.DataFrame(a[i]["chart"])
        b["date"] = pd.to_datetime(b["date"])
        b.set_index("date", inplace=True)
        b.columns = [i]
        if df is None:
            df = b
        else:
            df = df.join(b)
    dates = list(df.index.strftime("%Y-%m-%d"))
    print(type(df["SPY"][0]))
    return df, dates
