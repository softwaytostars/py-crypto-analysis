from unittest import TestCase

from tapy import Indicators

from Graphic import showAll
from SimulationDataRetriever import SimulationDataRetriever
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
        dataRetriever = SimulationDataRetriever(allSymbols)
        dataRetriever.retrieveAllDataWeekFrom("1 Jan, 2015")
        self.fit(dataRetriever.allDataFrame)

    def test_compute(self):
        allSymbols = ["BTCUSDT"]
        dataRetriever = SimulationDataRetriever(allSymbols)
        dataRetriever.retrieveAllDataWeekFrom("1 Jan, 2015")
        wallet = Wallet()
        wallet.addToWalletWithoutOrigin('USDT', 1)
        walletorig = wallet.copy()

        algo = AlgoTrading(dataRetriever, dataRetriever.allDataWeekFrame, allSymbols, wallet)

        dictBuySellOrders = {'opentime': [],
                             'buy': [],
                             'sell': []
                             }

        weekOpentimevalues = dataRetriever.allDataWeekFrame.index.get_level_values('opentime')
        startSimu = 50
        start = 0
        for opentime in weekOpentimevalues:
            start += 1
            if start <= startSimu:
                dictBuySellOrders['opentime'].append(opentime)
                dictBuySellOrders['sell'].append(0)
                dictBuySellOrders['buy'].append(0)
                continue

            (buyOrders, sellOrders) = algo.compute(opentime)
            self.assertTrue(len(buyOrders) <= 1)
            self.assertTrue(len(sellOrders) <= 1)
            dictBuySellOrders['opentime'].append(opentime)
            if len(buyOrders) >= 1:
                dictBuySellOrders['buy'].append(buyOrders[0].getPrice())
            else:
                dictBuySellOrders['buy'].append(0)
            if len(sellOrders) >= 1:
                dictBuySellOrders['sell'].append(sellOrders[0].getPrice())
            else:
                dictBuySellOrders['sell'].append(0)

            algo.executeOrders()
            print('wallet :')
            print(wallet)

        # Bilan:
        for curr in (set(walletorig.currentStock.keys()) & set(wallet.currentStock.keys())):
            amountorig = walletorig.amountForCurrency(curr)
            currentamount = wallet.amountForCurrency(curr)
            print("currency : % s, Before : % 5.7f, After : % 5.7f, Diff % 2.2f " % (
                curr, amountorig, currentamount, 100 * (currentamount - amountorig) / amountorig))

        # self.showData(dataRetriever.allDataFrame, dictBuySellOrders)

    def getDataWeekFrame(self, startTime, endTime):
        return dataRetriever.retrieveAllDataDayFor(startTime,endTime)

    def test_compute2(self):
        allSymbols = ["BTCUSDT"]
        dataRetriever = SimulationDataRetriever(allSymbols)
        dataWeekFrame = dataRetriever.retrieveAllDataWeekFor("1 Jan, 2017", '')
        wallet = Wallet()
        wallet.addToWalletWithoutOrigin('USDT', 1)
        walletorig = wallet.copy()

        algo = AlgoTrading(allSymbols, wallet)

        dictBuySellOrders = {'opentime': [],
                             'buy': [],
                             'sell': []
                             }

        weekOpentimevalues = dataWeekFrame.index.get_level_values('opentime')
        intervalweek = weekOpentimevalues[1] - weekOpentimevalues[0] #604800000
        intervalDay = 86400000
        startSimu = 50
        start = 0
        allDataDayFrame = dataRetriever.retrieveAllDataDayFor(weekOpentimevalues[0], '')
        for lastweekopentime in weekOpentimevalues:
            allDataDayFrame = dataRetriever.retrieveAllDataDayFor(lastweekopentime - 5 * intervalweek,
                                                                       lastweekopentime + intervalweek)
            dayOpentimevalues = allDataDayFrame.index.get_level_values('opentime')
            for lastdayopentime in dayOpentimevalues:
                if lastdayopentime < lastweekopentime:
                    continue
                start += 1
                if start <= startSimu:
                    dictBuySellOrders['opentime'].append(lastdayopentime)
                    dictBuySellOrders['sell'].append(0)
                    dictBuySellOrders['buy'].append(0)
                    continue

                # ce sont les providers qui donneront ca
                dataWeekEvaluation = dataWeekFrame.loc[
                    dataWeekFrame.index.get_level_values('opentime') <= lastweekopentime]
                dataDayEvaluation = allDataDayFrame.loc[
                    allDataDayFrame.index.get_level_values('opentime') <= lastdayopentime]

                # calcul de l'algo
                (buyOrders, sellOrders) = algo.compute(dataWeekEvaluation, dataDayEvaluation, lastweekopentime,
                                                       lastdayopentime)

                self.assertTrue(len(buyOrders) <= 1)
                self.assertTrue(len(sellOrders) <= 1)
                dictBuySellOrders['opentime'].append(lastdayopentime)
                if len(buyOrders) >= 1:
                    dictBuySellOrders['buy'].append(buyOrders[0].getPrice())
                else:
                    dictBuySellOrders['buy'].append(0)
                if len(sellOrders) >= 1:
                    dictBuySellOrders['sell'].append(sellOrders[0].getPrice())
                else:
                    dictBuySellOrders['sell'].append(0)

                algo.executeOrders()
            print('wallet :')
            print(wallet)

        # Bilan:
        for curr in (set(walletorig.currentStock.keys()) & set(wallet.currentStock.keys())):
            amountorig = walletorig.amountForCurrency(curr)
            currentamount = wallet.amountForCurrency(curr)
            print("currency : % s, Before : % 5.7f, After : % 5.7f, Diff % 2.2f " % (
                curr, amountorig, currentamount, 100 * (currentamount - amountorig) / amountorig))
