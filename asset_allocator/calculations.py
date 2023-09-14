"""Contains functions for querying end of day stock data and performing a
simple local optimization on based on risk-adjusted returns of a given portfolio"""

import numpy as np
import pandas as pd
import scipy.optimize as spo
import yfinance as yf
from pandas_datareader import data as pdr

yf.pdr_override()  # configure pandas datareader to query yahoo finance


def get_port_data(  # pylint: disable=dangerous-default-value
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    benchmark: str,
    stocks=["AAPL"],  # type: ignore
) -> tuple[pd.DataFrame, list[str]]:
    """Wrapper for querying data through pandas datareader"""

    data_close_df: pd.DataFrame = pdr.get_data_yahoo(
        stocks + [benchmark], start=start_date, end=end_date
    )[
        "Close"
    ]  # type: ignore
    dates = list(data_close_df.index.strftime("%Y-%m-%d"))  # type: ignore
    return data_close_df, dates


def optimize_portfolio(  # pylint: disable=dangerous-default-value
    portfolio,
    benchmark="SPY",
    optimizer="sr",
    syms=["GOOG", "AAPL", "GLD", "XOM"],
):
    """local optimizer to determine portfolio allocation to maximize sharpe ratio,
    minimum volatility, or absolute return"""

    if optimizer == "mv":
        opt_flip = 1
    else:
        opt_flip = -1

    # set initial weights to be 1 / # of different symbols
    initial_weights = len(syms) * [1.0 / len(syms)]
    # Parameters for optimizer
    bounds = tuple((0, 1) for stock in range(len(syms)))
    constraints = {"type": "eq", "fun": lambda w: np.sum(w) - 1}
    ##############################

    prices = portfolio[syms]

    def statistics(weights):
        # load daily stock data on a given list of securities by symbols and date

        # normalize different security prices such that every stock starts at 0
        # and price movements are represented as percent figures
        normalized_returns = np.log(prices / prices.shift(1))
        weights = np.array(weights)

        exp_port_return = np.sum(normalized_returns.mean() * weights) * 252

        # volatility aka Standard Deviation
        # normalized_returns.cov() returns a len(sym) by len(sym) matrix representing
        # all the covariances between the different stocks
        exp_port_vola = np.sqrt(
            np.dot(weights.T, np.dot(normalized_returns.cov() * 252, weights))
        )
        ##################################################################

        sharpe_ratio = exp_port_return / exp_port_vola

        return {"ar": exp_port_return, "mv": exp_port_vola, "sr": sharpe_ratio}
        ##################################################################

    def min_function_sharpe(weights):
        return opt_flip * statistics(weights)[optimizer]
        ##################################################################

    # use scipy optimizer to find the distribution of weights that create the
    # most negative value (sharpe ratio * -1)
    # through the minimizer, Sequential Least Squares Programming.
    opts = spo.minimize(
        min_function_sharpe,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
    )

    # get values for the output
    allocs = list(map(lambda x: round(x, 2), opts["x"]))
    stat_results = statistics(allocs)

    volatility = stat_results["mv"]
    sharpe = stat_results["sr"]

    # compute average daily returns

    prices_norm = prices / prices.iloc[0]
    weighted_norm_returns = (prices_norm * allocs).sum(axis=1)

    prices_benchmark = portfolio[benchmark]
    # normalize around 1
    gen_plot = prices_benchmark / prices_benchmark.iloc[0]
    portfolio = (weighted_norm_returns).to_frame().join(gen_plot.to_frame())
    portfolio.columns = ["Portfolio", benchmark]

    return portfolio, allocs, portfolio["Portfolio"][-1] - 1, volatility, sharpe
