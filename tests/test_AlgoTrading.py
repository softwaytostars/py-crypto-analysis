from unittest import TestCase

from tapy import Indicators

from DataRetriever import DataRetriever
from Graphic import showAll
from Wallet import Wallet
from algo.AlgoTrading import AlgoTrading
import pandas as pd
from lmfit.models import LorentzianModel
import matplotlib.pyplot as plt


class TestAlgoTrading(TestCase):
    def showData(self, df, dictBuySell):
        # df = read_dataset("test.csv")
        # Dimensions of dataset
        df.reset_index(inplace=True)
        df = df.set_index('opentime')
        df = df.sort_index()  # sort by datetime

        df2 = pd.DataFrame(dictBuySell)
        df2 = df2.set_index('opentime')
        df2 = df2.sort_index()  # sort by datetime

        alldf = pd.concat([df, df2], axis=1)

        stock = alldf.copy()
        fast_ma = stock['Close'].ewm(span=12, min_periods=0, adjust=False, ignore_na=False).mean()
        slow_ma = stock['Close'].ewm(span=26, min_periods=0, adjust=False, ignore_na=False).mean()
        macd = fast_ma - slow_ma
        signal = macd.ewm(span=9, min_periods=0, adjust=False, ignore_na=False).mean()
        stock['macd'] = macd
        stock['macdh'] = macd - signal
        stock['macds'] = signal

        # https: // pypi.org / project / tapy /
        indicators = Indicators(alldf)
        indicators.awesome_oscillator()
        indicators.macd()
        stock['ao'] = indicators.df['ao']

        # lengthAO1 = 5
        # lengthAO2 = 34
        # AO = sma((High + Low) / 2, lengthAO1) - sma((High + Low) / 2, lengthAO2)
        #
        # stock = StockDataFrame.retype(alldf)
        # stock['macd'] = stock.get('macd')  # calculate MACD
        # stock['boll'] = stock.get('boll')  # calculate MACD

        showAll(stock)

    def fit(self, df):
        opentimevalues = df.index.get_level_values('opentime')
        intervalTime = opentimevalues[1] - opentimevalues[0]
        df.reset_index(inplace=True)
        df["x"] = pd.to_numeric(df["opentime"], downcast="float").div(intervalTime)
        indicators = Indicators(df)
        indicators.awesome_oscillator()
        indicators.macd()
        df['ao'] = indicators.df['ao']

        df = df.set_index('x')
        df = df.sort_index()  # sort by datetime
        data = df.loc[
            (df.index.get_level_values('x') >= 2550) &
            (df.index.get_level_values('x') <= 2562)]
        data.reset_index(inplace=True)

        # model = SplitLorentzianModel()
        # model = SkewedGaussianModel()
        # model = DonaichModel()
        model = LorentzianModel()
        params = model.guess(-data['ao'], x=data['x'])

        result = model.fit(-data['ao'], params, x=data['x'])

        result.plot_fit()

        print(result.fit_report())
        plt.show()

    def test_fit(self):
        allSymbols = ["BTCUSDT"]
        dataRetriever = DataRetriever(allSymbols)
        dataRetriever.retrieveAllDataWeekFor("1 Jan, 2015", None)
        self.fit(dataRetriever.allDataFrame)

    def test_compute(self):
        all_symbols = ["BTCUSDT"]
        data_retriever = DataRetriever(all_symbols)
        data_week_frame = data_retriever.retrieveAllDataWeekFor("1 Jan, 2015", None)
        wallet = Wallet()
        wallet.add_to_wallet_without_origin('USDT', 1)
        wallet_orig = wallet.copy()

        algo = AlgoTrading(all_symbols, wallet)

        dictBuySellOrders = {'opentime': [],
                             'buy': [],
                             'sell': []
                             }

        week_opentime_values = data_week_frame.index.get_level_values('opentime')
        interval_week = week_opentime_values[1] - week_opentime_values[0]

        start = 0
        for open_time in week_opentime_values:
            start += 1
            if start <= 50:
                dictBuySellOrders['opentime'].append(open_time)
                dictBuySellOrders['sell'].append(0)
                dictBuySellOrders['buy'].append(0)
                continue

            # retrieve the 10 last weeks datas
            start_data_open_time = open_time - 10 * interval_week
            data_last_weeks = data_week_frame.loc[
                (data_week_frame.index.get_level_values('opentime') <= open_time) &
                (data_week_frame.index.get_level_values('opentime') > start_data_open_time)]

            data_last_days = data_retriever.retrieveAllDataDayFor(start_data_open_time, open_time)
            currentData = data_last_weeks.loc[data_last_weeks.index.get_level_values('opentime') == open_time]
            current_price = currentData['Open'].tail(1).values[0]
            current_date = str(currentData['datetime'].tail(1).values[0])
            (buyOrders, sellOrders) = algo.compute(data_last_weeks, data_last_days, current_price, current_date)
            self.assertTrue(len(buyOrders) <= 1)
            self.assertTrue(len(sellOrders) <= 1)
            dictBuySellOrders['opentime'].append(open_time)
            if len(buyOrders) >= 1:
                dictBuySellOrders['buy'].append(buyOrders[0].getPrice())
            else:
                dictBuySellOrders['buy'].append(0)
            if len(sellOrders) >= 1:
                dictBuySellOrders['sell'].append(sellOrders[0].getPrice())
            else:
                dictBuySellOrders['sell'].append(0)

            algo.execute_orders()

        # Bilan:
        for curr in (set(wallet_orig.currentStock.keys()) & set(wallet.currentStock.keys())):
            amountorig = wallet_orig.amount_for_currency(curr)
            currentamount = wallet.amount_for_currency(curr)
            print("currency : % s, Before : % 5.7f, After : % 5.7f, Diff % 2.2f " % (
                curr, amountorig, currentamount, 100 * (currentamount - amountorig) / amountorig))

        # self.showData(data_retriever.allDataFrame, dictBuySellOrders)