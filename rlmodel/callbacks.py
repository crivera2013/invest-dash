"""Contains the callback logic for all the data being rendered
on the UI for the RL model tab"""

import json

import pandas as pd
from dash import Input, Output, State
from plotly.graph_objs import Layout, Scatter

from rlmodel import calculations


def get_callbacks(app):
    """wrapper functioon to assign all the callbacks
    for the Reinforcement Learning tab to the app object"""

    @app.callback(
        Output(component_id="hidden-rl-data", component_property="children"),
        [Input(component_id="rl-button", component_property="n_clicks")],
        [
            State(component_id="train-rl-date-ranger", component_property="start_date"),
            State(component_id="train-rl-date-ranger", component_property="end_date"),
            State(component_id="test-rl-date-ranger", component_property="start_date"),
            State(component_id="test-rl-date-ranger", component_property="end_date"),
            State("rl-stock-picker", "value"),
        ],
    )
    def getRLData(n_clicks, train_start, train_end, test_start, test_end, ticker):
        if n_clicks is not None:
            stocks = calculations.qLearning(
                symbol=ticker,
                train_sd=train_start,
                train_ed=train_end,
                test_sd=test_start,
                test_ed=test_end,
                impact=0.0,
                commission=0.0,
                epochs=100,
                dyna=5,
                sv=100000,
            )

            # stocks.reset_index(inplace=True)
            # results['Date'] = results['Date'].dt.strftime('%Y-%m-%d')
            dates = list(stocks.index.strftime("%Y-%m-%d"))
            stocks = stocks.to_dict("records")

            results = dict(dates=dates, stocks=stocks)

            return json.dumps(results)
        else:
            return "hold"

    @app.callback(Output("rl-datatable", "data"), [Input("hidden-rl-data", "children")])
    def tableTime(values):
        values = json.loads(values)

        values = values["stocks"]

        print(values[-1])
        print(type(values[-1]))

        qReturns = (
            str(
                round((values[-1]["Q Learning"] / values[0]["Q Learning"] - 1) * 100, 2)
            )
            + "%"
        )
        regReturns = (
            str(round((values[-1]["Benchmark"] / values[0]["Benchmark"] - 1) * 100, 2))
            + "%"
        )

        record = {"Q Learner": qReturns, "Buy and Hold": regReturns}

        print(record)

        return [record]

    @app.callback(
        Output(component_id="rl-graph", component_property="figure"),
        [Input("hidden-rl-data", "children")],
    )
    def RLgraph(values):
        values = json.loads(values)

        dates = values["dates"]

        portfolio = pd.DataFrame(values["stocks"])

        portfolio["Date"] = pd.to_datetime(dates, format="%Y-%m-%d")
        portfolio.set_index("Date", inplace=True)
        traces = []

        traces.append(
            Scatter(
                x=portfolio.index,
                y=portfolio["Q Learning"],
                # text=df_by_continent['country'],
                opacity=0.7,
                mode="lines",
                line=dict(
                    color="light Green",
                ),
                name="Q Learning",
            )
        )

        traces.append(
            Scatter(
                x=portfolio.index,
                y=portfolio["Benchmark"],
                # text=df_by_continent['country'],
                opacity=0.7,
                mode="lines",
                line=dict(
                    color="light Blue",
                ),
                name="Buy and Hold",
            )
        )

        layout = Layout(
            title="Naive Q Learner vs Buy and Hold",
            yaxis={"title": "Normalized Price ($)"},
            hovermode="closest",
            legend=dict(x=0, y=1),
        )

        results = {"data": traces, "layout": layout}

        return results
