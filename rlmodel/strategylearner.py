import datetime as dt

import numpy as np
import pandas as pd

from rlmodel import qlearner as ql


from Indicators import getIndicatorData


class StrategyLearner(object):
    # constructor
    def __init__(self, verbose=False, impact=0.0, dyna=20, epochs=200):
        self.verbose = verbose
        self.impact = impact
        self.model = None
        self.results = None
        self.dyna = dyna
        self.epochs = epochs
        self.data = None
        self.symbol = None

    # this method should create a Qmodel, and train it for trading
    def addEvidence(
        self,
        symbol: str = "IBM",
        sd: pd.Timestamp = pd.Timestamp("2008-01-01"),
        ed: pd.Timestamp = pd.Timestamp("2009-12-31"),
    ):
        # add your code to do learning here
        data = getIndicatorData(symbol, sd, ed)

        data = self.Discretize(data, symbol)
        self.data = data
        self.symbol = symbol

        num_states = int("22221", 3) * 5  # (52*5) # data.shape[0]
        num_actions = 3

        print("number of state: {0}".format(num_states))

        self.model = ql.QLearner(
            num_states=num_states,
            num_actions=num_actions,
            alpha=0.1,
            gamma=0.9,
            rar=0.9995,
            radr=0.9995,
            dyna=self.dyna,
            verbose=False,
        )  # initialize the model

        # p = multiprocessing.Pool(multiprocessing.cpu_count())

        # p.map(self.trainRLGame2, range(self.epochs))

        self.trainRLGame(data, symbol, self.epochs, 200)

    # this method should use the existing policy and test it against new data
    def testPolicy(
        self,
        symbol="IBM",
        sd=dt.datetime(2009, 1, 1),
        ed=dt.datetime(2010, 1, 1),
        sv=10000,
    ):
        df = getIndicatorData(symbol, sd, ed)
        df = self.Discretize(df, symbol)
        print(self.model.rar)
        self.model.rar = 0.0
        game = self.testRLGame(df, symbol)

        game["trades1"] = np.where(game["trades"] == 0, -1, 5)
        game["trades1"] = np.where(game["trades"] == 1, 0, game["trades1"])
        game["trades1"] = np.where(game["trades"] == 2, 1, game["trades1"])
        game["amount"] = game["trades1"] - game["trades1"].shift(1)
        game["shares"] = 1000 * game["amount"]
        game["shares"] = np.where(
            pd.isnull(game["shares"]), game["trades1"] * 1000, game["shares"]
        )
        game["Symbol"] = symbol
        game = game[[symbol, "Symbol", "shares"]]
        game["cash"] = 1.0

        game = game.to_dict("records")
        cash = sv
        position = 0
        for row in game:
            position = position + row["shares"]
            cash = cash - row[symbol] * row["shares"]
            row["cash"] = cash
            row["position"] = position
            row["portfolio"] = row["cash"] + row["position"] * row[symbol]
        game = pd.DataFrame(game)
        game["date"] = df.index

        self.results = game

        trades = game[["date", "shares"]]
        trades.set_index("date", inplace=True)

        return trades

    def trainRLGame(self, marketHistory, symbol, epochs=100, show_score=50):
        market = marketHistory.copy()
        market.reset_index(inplace=True)
        market = market.to_dict("records")
        for epoch in range(epochs):
            # day_counter = 1

            state0 = int(market[0]["discrete"] + "0", 3) * (
                market[0]["Date"].weekday() + 1
            )  # * (market[0]['Date'].week * 5 + market[0]['Date'].weekday())
            # day_counter += 1

            previous_result = market[0][symbol]
            action = self.model.querysetstate(state0)

            total_reward = 0
            for day in market[1:]:
                reward, previous_result = self.GetReward(
                    previous_result, day[symbol], action
                )
                total_reward += reward
                state = int(day["discrete"] + str(action), 3) * (
                    market[0]["Date"].weekday() + 1
                )  # * (day['Date'].week * 5 + day['Date'].weekday())
                # day_counter += 1
                action = self.model.query(state, reward)

                # if day_counter > 252:
                #    day_counter = 1

            if epoch % 50 == 0:
                print("Epoch at: %s" % epoch)
                print("rar is: %s" % self.model.rar)

            # if epoch % show_score == 0:
            #    print(total_reward)

    def trainRLGame2(self, epoch):
        marketHistory = self.data.to_dict("records")
        day_counter = 1

        state0 = int(marketHistory[0]["discrete"] + "0", 3) * day_counter
        day_counter += 1

        previous_result = marketHistory[0][self.symbol]
        action = self.model.querysetstate(state0)

        total_reward = 0
        for day in marketHistory[1:]:
            reward, previous_result = self.GetReward(
                previous_result, day[self.symbol], action
            )
            total_reward += reward
            state = int(day["discrete"] + str(action), 3) * day_counter
            day_counter += 1
            action = self.model.query(state, reward)

            if day_counter > 252:
                day_counter = 1

        if epoch % 250 == 0:
            print("Epoch at: %s" % epoch)

        # if epoch % show_score == 0:
        #    print(total_reward)

    def testRLGame(self, tradelist, column):
        market = tradelist.copy()
        market.reset_index(inplace=True)
        market = market.to_dict("records")
        decisions = []
        # day_counter = 1

        state0 = int(market[0]["discrete"] + "0", 3) * (
            market[0]["Date"].weekday() + 1
        )  # (market[0]['Date'].week * 5 + market[0]['Date'].weekday())
        # day_counter +=1
        self.model.rar = 0.0
        action = self.model.querysetstate(state0)
        decisions.append(action)

        for day in market[1:]:
            state = int(day["discrete"] + str(action), 3) * (
                day["Date"].weekday() + 1
            )  # (day['Date'].week * 5 + day['Date'].weekday())
            # day_counter +=1
            action = self.model.querysetstate(state)

            decisions.append(action)

            # if day_counter > 252:
            #    day_counter = 1

        tradelist["trades"] = decisions
        return tradelist

    def GetReward(self, yesterday, today, action):
        if action == 0:
            reward = yesterday - (today + today * self.impact) * 1.5
        elif action == 1:
            reward = yesterday - today
        elif action == 2:
            reward = (today - today * self.impact) - yesterday

        # if action != 0:
        yesterday = today

        return reward, yesterday

    def Discretize(self, df, symbol):
        # 0 = sell, 1 = hold, 2 = buy
        df["bol signal"] = np.where(df[symbol] >= df["Upper Band"], 0, 1)
        df["bol signal"] = np.where(df[symbol] <= df["Lower Band"], 2, df["bol signal"])

        # rsi is considered overbought when above 70 and oversold when below 30
        # 0 = sell, 1 = hold, 2 = buy
        df["rsi signal"] = np.where(df["RSI"] > 70, 0, 1)
        df["rsi signal"] = np.where(df["RSI"] < 30, 2, df["bol signal"])

        # an OBV version of the bollinger bands tracking volume with 1.5 standard deviation bands
        # 0 = sell, 1 = hold, 2 = buy
        df["obv signal"] = np.where(df["OBV"] >= df["OBV Upper Band"], 0, 1)
        df["obv signal"] = np.where(
            df["OBV"] <= df["OBV Lower Band"], 2, df["obv signal"]
        )

        # The MACD: buy signal when above its own nine-day EMA;  sell when moves below its nine-day EMA.
        # buy = 1, sell = 0
        df["macd signal"] = np.where(df["MACD"] > df["9 ema MACD"], 1, 0)

        df = df[["bol signal", "rsi signal", "obv signal", "macd signal", symbol]]

        for col in df:
            if col != symbol:
                df[col] = df[col].apply(str)

        df["discrete"] = (
            df["bol signal"] + df["rsi signal"] + df["obv signal"] + df["macd signal"]
        )

        return df
