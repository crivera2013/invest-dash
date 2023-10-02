import numpy as np
import pandas as pd

from rlmodel import strategylearner as sl
import Indicators as ind


import yfinance as yf
from pandas_datareader import data as pdr

yf.pdr_override()  # configure pandas datareader to query yahoo finance


def get_stock_data(  # pylint: disable=dangerous-default-value
    start_date: pd.Timestamp,
    end_date: pd.Timestamp,
    ticker: str = "AAPL",  # type: ignore
) -> pd.DataFrame:
    """Wrapper for querying data through pandas datareader"""

    data_close_df: pd.DataFrame = pdr.get_data_yahoo(
        ticker, start=start_date, end=end_date
    )[
        ["Adj Close", "Volume"]
    ]  # type: ignore
    return data_close_df


def compute_portvals(
    symbol: str = "JPM",
    start_date: pd.Timestamp = pd.Timestamp("2010-01-01"),
    end_date: pd.Timestamp = pd.Timestamp("2011-12-31"),
    orders: pd.DataFrame = pd.DataFrame(),
    start_val: float = 100000.0,
    commission: float = 9.95,
    impact: float = 0.005,
):
    prices: pd.DataFrame = get_stock_data(start_date, end_date, symbol)
    prices.dropna(inplace=True)
    # get all stock symbols

    prices["cash"] = 1.0
    orders["multiplier"] = orders["Order"].apply(lambda x: 1.0 if x == "BUY" else -1.0)
    orders["Shares"] = orders["Shares"] * orders["multiplier"]
    orders.drop(["Order", "multiplier"], axis=1, inplace=True)

    # !!! TRADES HAS TO BE A GROUP BY AND NOT PIVOT TABLE!!!
    b = (
        orders.groupby([orders.index.get_level_values(0), "Symbol"])[["Shares"]]
        .sum()
        .reset_index()
    )
    b.columns = ["Date", "Symbol", "Shares"]
    b.set_index("Date", inplace=True)
    trades = b.pivot_table(
        values="Shares", index=["Date"], columns=["Symbol"], fill_value=0
    )

    # trades = orders.pivot_table(values='Shares', index=['Date'], columns=['Symbol'],fill_value=0)
    empty = pd.DataFrame(index=prices.index)
    trades = pd.merge(empty, trades, how="left", left_index=True, right_index=True)
    trades.fillna(0, inplace=True)
    trades = trades[sorted(trades.columns)]

    x = orders.reset_index().values
    trades["cash"] = 0.0

    for i in x:
        trades.at[i[0], "cash"] += -(
            i[1] * prices.at[i[0], symbol]
            + commission
            + abs(i[1] * prices.at[i[0], symbol] * impact)
        )

    holdings = trades.copy()
    holdings.iloc[0, -1] = start_val + trades.iloc[0, -1]
    holdings = holdings.cumsum()

    values = prices * holdings

    portval = pd.DataFrame(values.sum(axis=1))

    portval.columns = ["manual"]

    return portval, values, holdings, trades, prices


def benchmarking(symbol="JPM", sd="2010-01-01", ed="2011-12-31", start_val=100000.0):
    prices = ind.getStock(symbol, sd, ed)
    prices.dropna(inplace=True)

    prices["bench"] = 1000.0 * prices[symbol]
    prices["bench"] = prices["bench"] + (start_val - 1000.0 * prices[symbol][0])
    prices["Benchmark"] = prices["bench"] / prices["bench"][0]
    benchmark_cr = round(
        ((prices["Benchmark"][-1] / prices["Benchmark"][0]) - 1) * 100.0, 3
    )

    prices["normal"] = np.log(prices["bench"] / prices["bench"].shift(1))

    bench = prices[["Benchmark"]]
    return bench, benchmark_cr


def qLearning(
    symbol="JPM",
    train_sd: pd.Timestamp = pd.Timestamp("2008-01-01"),
    train_ed: pd.Timestamp = pd.Timestamp("2009-12-13"),
    test_sd: pd.Timestamp = pd.Timestamp("2010-01-01"),
    test_ed: pd.Timestamp = pd.Timestamp("2011-12-31"),
    impact: float = 0.0,
    commission: float = 0.0,
    epochs: int = 100,
    dyna: int = 20,
    sv: int = 100000,
):
    learner = sl.StrategyLearner(verbose=False, impact=0.0, dyna=dyna, epochs=epochs)
    learner.addEvidence(
        symbol=symbol, sd=train_sd, ed=train_ed, sv=sv
    )  # training phase

    df_trades = learner.testPolicy(symbol=symbol, sd=test_sd, ed=test_ed, sv=sv)
    df_trades = df_trades[df_trades["shares"] != 0]
    df_trades["Order"] = np.where(df_trades["shares"] > 0, "BUY", "SELL")
    df_trades["Symbol"] = symbol
    df_trades.columns = ["Shares", "Order", "Symbol"]
    df_trades["Shares"] = df_trades["Shares"].abs()

    ql_out, values, holdings, trades, prices = compute_portvals(
        symbol, test_sd, test_ed, df_trades, sv, commission=commission, impact=impact
    )

    ql_out.columns = ["Q Learning"]

    benchmark, benchmark_cr = benchmarking(
        symbol=symbol, sd=test_sd, ed=test_ed, start_val=sv
    )

    benchmark.columns = ["Benchmark"]

    ql_out_cr = round(
        ((ql_out["Q Learning"][-1] / ql_out["Q Learning"][0]) - 1) * 100.0, 3
    )

    ql_out["Q Learning"] = ql_out["Q Learning"] / ql_out["Q Learning"][0]

    print("*****************")
    print("Out Sample")
    print(
        "Buy-and-Hold strategy return for out-sample data is: "
        + str(benchmark_cr)
        + "%"
    )
    print("Q Learning strategy return for out-sample data is: " + str(ql_out_cr) + "%")
    print("\n")

    return ql_out.join(benchmark)  # ql_out, ql_out_cr, benchmark, benchmark_cr
