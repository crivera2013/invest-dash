"""Contains the callback logic for all the data being rendered on the UI"""

import json

import pandas as pd
from dash import Input, Output
from plotly.graph_objs import Layout, Scatter

from asset_allocator import calculations


def get_callbacks(app):
    """wrapper functioon to assign all the callbacks for the asset_allocator tab
    to the app object"""

    @app.callback(
        Output(component_id="the-graph", component_property="figure"),
        [Input("hidden-table-data", "children")],
    )
    def plot_line_graph(values):
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

        results = {"data": traces, "layout": layout}

        return results

    @app.callback(Output("datatable", "data"), [Input("hidden-table-data", "children")])
    def update_allocations_table(values):
        values = json.loads(values)
        stocks = values["stocks"]
        print(stocks)
        allocations = values["allocations"]
        allocations = [str(round(i * 100, 2)) + "%" for i in allocations]

        return pd.DataFrame(columns=stocks, data=[allocations]).to_dict("records")

    @app.callback(
        Output(component_id="hidden-graph-data", component_property="children"),
        [
            Input(component_id="date-ranger", component_property="value"),
            Input(component_id="stock-picker", component_property="value"),
            Input(component_id="benchmarker", component_property="value"),
        ],
    )
    def query_eod_data(date_lookback: str, stocks: list[str], benchmark: str) -> dict:
        end_date = pd.Timestamp.now()
        if date_lookback == "6m":
            start_date = end_date - pd.DateOffset(months=6)
        elif date_lookback == "ytd":
            start_date = pd.Timestamp(end_date.year, 1, 1)
        elif date_lookback == "1y":
            start_date = end_date - pd.DateOffset(years=1)
        elif date_lookback == "2y":
            start_date = end_date - pd.DateOffset(years=2)
        else:
            raise ValueError("Invalid date range")

        initial_port, dates = calculations.get_port_data(
            start_date, end_date, benchmark, stocks
        )
        initial_port = initial_port.to_dict("records")

        result: dict = dict(initial_port=initial_port, dates=dates, stocks=stocks)

        return json.dumps(result)  # type: ignore

    @app.callback(
        Output(component_id="hidden-table-data", component_property="children"),
        [
            Input("hidden-graph-data", "children"),
            Input(component_id="benchmarker", component_property="value"),
            Input(component_id="optimizer", component_property="value"),
        ],
    )
    def convert_data_to_dict_format(values, benchmark, optimizer):
        values = json.loads(values)

        initial_port = pd.DataFrame(values["initial_port"])
        initial_port["Date"] = pd.to_datetime(values["dates"], format="%Y-%m-%d")
        initial_port.set_index("Date", inplace=True)

        (
            portfolio,
            allocs,
            port_return,
            volatility,
            sharpe,
        ) = calculations.optimize_portfolio(
            initial_port, benchmark, optimizer, values["stocks"]
        )
        print(values["stocks"])

        result = dict(
            portfolio=portfolio.to_dict("records"),
            allocations=allocs,
            port_return=port_return,
            volatility=volatility,
            sharpe=sharpe,
            benchmark=benchmark,
            dates=values["dates"],
            stocks=values["stocks"],
        )

        return json.dumps(result)
