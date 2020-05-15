from Graphic import showAll
from SimulationDataRetriever import SimulationDataRetriever
from Wallet import Wallet
from algo.AlgoTrading import AlgoTrading
import pandas as pd


class BilanWallet(object):
    def __init__(self, period, walletorig, dataDayOrig):
        self.period = period
        self.walletorig = walletorig
        self.dataDayOrig = dataDayOrig
        self.endWallet = None

    def setEndWallet(self, wallet, endDataDay):
        self.endWallet = wallet
        self.endDataDay = endDataDay

    def __equivalentUSDTForWallet__(self, wallet, dataDay):
        totalEquivalentAmountUSDT = 0
        for curr in wallet.currentStock.keys():
            amount = wallet.amountForCurrency(curr)
            if curr == "USDT":
                totalEquivalentAmountUSDT += amount
            else:
                lastPriceInUsdt = dataDay['Close'].tail(1).values[0] #TODO chopper pour le symbol currency+USDT
                totalEquivalentAmountUSDT += lastPriceInUsdt*amount
        return totalEquivalentAmountUSDT

    def bilan(self):
        totalEquivalentAmountUSDTOrig = self.__equivalentUSDTForWallet__(self.walletorig, self.dataDayOrig)
        totalEquivalentAmountUSDT = self.__equivalentUSDTForWallet__(self.endWallet, self.endDataDay)
        print("Bilan USDT for %s : Before : % 5.7f , After : %5.7f, rapport : %5.7f" %
              (self.period, totalEquivalentAmountUSDTOrig, totalEquivalentAmountUSDT, totalEquivalentAmountUSDT/totalEquivalentAmountUSDTOrig))
        return totalEquivalentAmountUSDT/totalEquivalentAmountUSDTOrig



class Simulator(object):
    def __init__(self, allSymbols):
        self.allSymbols = allSymbols
        self.dataRetriever = SimulationDataRetriever(allSymbols)
        self.dataDayFrame = None
        self.dataWeekFrame = self.dataRetriever.retrieveAllDataWeekFor("01 Jan, 2014", '')

    def retrieveDataDayFrameIfNeeded(self, opentime):
        # si pas encore defini ou bien que le last index correspond à opentime
        if (self.dataDayFrame is None) or (self.dataDayFrame.index[-2] <= opentime):
            self.dataDayFrame = self.dataRetriever.retrieveAllDataDayFor(opentime, '')
        return self.dataDayFrame

    def showData(self, dictBuySell):
        # df = read_dataset("test.csv")
        # Dimensions of dataset
        # df.reset_index(inplace=True)
        # df = df.set_index('opentime')
        # df = df.sort_index()  # sort by datetime

        df2 = pd.DataFrame(dictBuySell)
        df2 = df2.set_index('opentime')
        df2 = df2.sort_index()  # sort by datetime

        # alldf = pd.concat([df, df2], axis=1)

        showAll(df2, True, 'day.html')

    def getPeriodCheck(self, date, yearCheckWallets):
        for yearPeriod in yearCheckWallets:
            if date.startswith(yearPeriod):
                return yearPeriod
        return None

    def runSimu(self, wallet):
        yearCheckWallets = ['2017',
                            '2018',
                            '2019',
                            '2020']
        dictWalletsByYear = {}
        previousPeriod = None

        algo = AlgoTrading(self.allSymbols, wallet)

        dictBuySellOrders = {'opentime': [],
                             'Open': [],
                             'Close': [],
                             'buy': [],
                             'sell': [],
                             'SAR': [],
                             'ao': [],
                             'macd_histo': [],
                             'macd_value': [],
                             'macd_signal': [],
                             'tauxtsi': [],
                             'tsi': []
                             }

        weekOpentimevalues = self.dataWeekFrame.index.get_level_values('opentime')
        intervalweek = weekOpentimevalues[1] - weekOpentimevalues[0]  # 604800000
        # intervalDay = 86400000
        self.retrieveDataDayFrameIfNeeded(weekOpentimevalues[0])
        lastDataForDay = None
        for lastweekopentime in weekOpentimevalues:
            self.retrieveDataDayFrameIfNeeded(lastweekopentime - 5 * intervalweek)
            dayOpentimevalues = self.dataDayFrame.loc[
                (self.dataDayFrame.index.get_level_values('opentime') >= lastweekopentime) &
                (self.dataDayFrame.index.get_level_values('opentime') < (
                            lastweekopentime + intervalweek))].index.get_level_values(
                'opentime')
            for lastdayopentime in dayOpentimevalues:
                if lastdayopentime < lastweekopentime:
                    continue
                dataForDay = self.dataDayFrame.loc[
                    self.dataDayFrame.index.get_level_values('opentime') == lastdayopentime]
                lastCloseprice = dataForDay['Close'].values[0]
                lastOpenprice = dataForDay['Open'].values[0]
                if self.dataWeekFrame.iloc[(self.dataWeekFrame.index.get_level_values('opentime') == lastweekopentime)][
                    'ao'].isnull().values[0]:
                    dictBuySellOrders['opentime'].append(lastdayopentime)
                    dictBuySellOrders['Close'].append(lastCloseprice)
                    dictBuySellOrders['Open'].append(lastOpenprice)
                    dictBuySellOrders['sell'].append(-100)
                    dictBuySellOrders['buy'].append(-100)
                    dictBuySellOrders['SAR'].append(-100)
                    dictBuySellOrders['ao'].append(-100)
                    dictBuySellOrders['macd_histo'].append(-100)
                    dictBuySellOrders['macd_value'].append(-100)
                    dictBuySellOrders['macd_signal'].append(-100)
                    dictBuySellOrders['tauxtsi'].append(-100)
                    dictBuySellOrders['tsi'].append(-100)
                    continue

                # ce sont les providers qui donneront ca
                dataWeekEvaluation = self.dataWeekFrame.loc[
                    self.dataWeekFrame.index.get_level_values('opentime') <= lastweekopentime]
                # strictly because we will make decision from previous day
                dataDayEvaluation = self.dataDayFrame.loc[
                    self.dataDayFrame.index.get_level_values('opentime') < lastdayopentime]

                date = str(dataDayEvaluation['datetime'].tail(1).values[0])
                period = self.getPeriodCheck(date, yearCheckWallets)
                if period is not None and (previousPeriod is None or period != previousPeriod):
                    dictWalletsByYear[period] = BilanWallet(period, wallet.copy(), dataDayEvaluation.copy())
                    if previousPeriod is not None:
                        dictWalletsByYear.get(previousPeriod).setEndWallet(wallet.copy(), dataDayEvaluation.copy())
                    previousPeriod = period
                lastDataForDay = dataDayEvaluation.copy()

                # calcul de l'algo
                (buyOrders, sellOrders) = algo.compute(dataWeekEvaluation, dataDayEvaluation, lastweekopentime,
                                                       lastdayopentime)

                # self.assertTrue(len(buyOrders) <= 1)
                # self.assertTrue(len(sellOrders) <= 1)
                dictBuySellOrders['opentime'].append(lastdayopentime)
                dictBuySellOrders['Close'].append(lastCloseprice)
                dictBuySellOrders['Open'].append(lastOpenprice)
                dictBuySellOrders['SAR'].append(dataForDay['SAR'].values[0])
                dictBuySellOrders['ao'].append(dataForDay['ao'].values[0])
                dictBuySellOrders['macd_histo'].append(dataForDay['macd_histo'].values[0])
                dictBuySellOrders['macd_value'].append(dataForDay['macd_value'].values[0])
                dictBuySellOrders['macd_signal'].append(dataForDay['macd_signal'].values[0])
                dictBuySellOrders['tauxtsi'].append(dataForDay['tauxtsi'].values[0])
                dictBuySellOrders['tsi'].append(dataForDay['tsi'].values[0])
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
        # for curr in (set(walletorig.currentStock.keys()) & set(wallet.currentStock.keys())):
        #     amountorig = walletorig.amountForCurrency(curr)
        #     currentamount = wallet.amountForCurrency(curr)
        #     print("currency : % s, Before : % 5.7f, After : % 5.7f, Diff % 2.2f " % (
        #         curr, amountorig, currentamount, 100 * currentamount / amountorig))
        # for curr in walletorig.currentStock.keys():
        #     amountorig = walletorig.amountForCurrency(curr)
        #     currentamount = wallet.amountForCurrency(curr)
        #     if amountorig > 0:
        #         print("currency : % s, Before : % 5.7f, After : % 5.7f, Diff % 2.2f " % (
        #             curr, amountorig, currentamount, 100 * currentamount / amountorig))
        #     else:
        #         print("currency : % s, Before : % 5.7f, After : % 5.7f " % (
        #             curr, amountorig, currentamount))

        # if last period
        if previousPeriod == yearCheckWallets[len(yearCheckWallets) - 1]:
            dictWalletsByYear.get(previousPeriod).setEndWallet(wallet.copy(), lastDataForDay)

        result = []
        for period in dictWalletsByYear.keys():
            result.append(dictWalletsByYear.get(period).bilan())

        self.showData(dictBuySellOrders)
        showAll(self.dataWeekFrame, False, "week.html")
        return result
