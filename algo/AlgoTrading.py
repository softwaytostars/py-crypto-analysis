from tapy import Indicators

from Model import Side
from OrderMaker import OrderMaker
from Utils import getFromToCurrencies, sortByProfit, profitForSell, getFromCurrency, sortByProba, getToCurrency
from evaluators.EvaluatorBuy import EvaluatorBuy
from evaluators.EvaluatorSell import EvaluatorSell
from indicators.psar import psar


class AlgoTrading(object):
    def __init__(self, allSymbols, wallet):
        self.allSymbols = allSymbols
        self.wallet = wallet
        self.allDataDayFrame = None
        self.allDataWeekFrame = None
        self.ordermaker = OrderMaker(wallet)
        self.periodsToUseForEvaluation = 30
        self.intervalweek = 0

    def __retrieveDataForEvaluation__(self, lastweekopentime, symbol):
        # look for the first opentime available for the symbol
        # firstopentime = \
        #     allDataFrame.loc[(allDataFrame.index.get_level_values('symbol') == symbol)].index.get_level_values(
        #         'opentime')[
        #         0]
        self.allDataWeekFrame = self.dataRetriever.retrieveAllDataWeekFor(
            lastweekopentime - self.periodsToUseForEvaluation * self.intervalweek,
            lastweekopentime + self.intervalweek)

        self.allDataDayFrame = self.dataRetriever.retrieveAllDataDayFor(lastweekopentime,
                                                                        lastweekopentime + self.intervalweek)

        # dataOld = self.allDataFrame.loc[
        #     (self.allDataFrame.index.get_level_values('opentime') <= lastweekopentime + intervalweek) &
        #     (self.allDataFrame.index.get_level_values('symbol') == symbol)]

    # fast_ma = stock['Close'].ewm(span=12, min_periods=0, adjust=False, ignore_na=False).mean()
    # slow_ma = stock['Close'].ewm(span=26, min_periods=0, adjust=False, ignore_na=False).mean()
    # macd = fast_ma - slow_ma
    # signal = macd.ewm(span=9, min_periods=0, adjust=False, ignore_na=False).mean()
    # stock['macd'] = macd
    # stock['macdh'] = macd - signal
    # stock['macds'] = signal

    # stock['SAR'] = talib.SAR(stock.High, stock.Low, acceleration=0.02, maximum=0.2)
    # indicators = Indicators(alldf)
    # indicators.awesome_oscillator()
    # indicators.macd()
    # stock['ao'] = indicators.df['ao']

    # fast_length = input(title="Fast Length", type=input.integer, defval=12)
    # slow_length = input(title="Slow Length", type=input.integer, defval=26)
    # src = input(title="Source", type=input.source, defval=Close)
    # signal_length = input(title="Signal Smoothing", type=input.integer, minval=1, maxval=50, defval=9)
    # fast_ma = sma_source ? sma(src, fast_length): ema(src, fast_length)
    # slow_ma = sma_source ? sma(src, slow_length): ema(src, slow_length)
    # macd = fast_ma - slow_ma
    # signal = sma_signal ? sma(macd, signal_length): ema(macd, signal_length)
    # hist = macd - signal
    # compute indicators for this data
    # stock = StockDataFrame.retype(dataOld)
    # stock['macd'] = stock.get('macd')  # calculate MACD
    # stock['boll'] = stock.get('boll')  # calculate MACD

    def compute(self, dataWeekEvaluation, dataDayEvaluation, lastweekopentime,
                lastdayopentime):
        sellOrders = []
        buyOrders = []

        dictEvalBuy = {}
        dictEvalSell = {}
        buyablenow = []
        cannotbuy = []
        willbesold = []

        currentPrice = dataDayEvaluation['Close'].tail(1).values[0]  # TODO should be true currentprice instead if not simu
        evaluatorBuy = EvaluatorBuy(dataWeekEvaluation, dataDayEvaluation, currentPrice)
        evaluatorSell = EvaluatorSell(dataWeekEvaluation, dataDayEvaluation, currentPrice)

        # determine evaluation buy/sell for reach symbol
        for symbol in self.allSymbols:
            dictEvalBuy[symbol] = evaluatorBuy.evaluateBuy()
            dictEvalSell[symbol] = evaluatorSell.evaluateSell()
            # what can we buy ?
            (fromcurr, tocurr) = getFromToCurrencies(symbol)
            # should sell if probability is greater than 70% (# parametre à optimiser)
            shouldBeSold = dictEvalSell.get(symbol).proba > 0.70
            # should buy if probability is greater than (# parametre à optimiser)
            shouldBeBought = dictEvalBuy.get(symbol).proba > 0.60
            # on veut revendre dans la même currency d'achat à moins que ce soit pour acheter quelque chose qu'on ne peut
            # pas avoir mais ca sera plus + tard (cf gestion cannotbuy)
            # and currentStock.get(fromcurr).frompairorigin == symbol
            if shouldBeSold and self.wallet.amountForCurrency(fromcurr) > 0:
                willbesold.append(symbol)
            if shouldBeBought:
                if self.wallet.amountForCurrency(tocurr) > 0:
                    buyablenow.append(symbol)
                else:
                    cannotbuy.append(symbol)

        # put orders (priority to sell orders to make profit now) on veut revendre dans la même currency d'achat à moins
        # que ce soit pour acheter quelque chose qu'on ne peut pas avoir mais ca sera plus + tard (cf gestion )cannotbuy
        sortByProfit(willbesold, dictEvalSell, self.wallet)
        for symbol in willbesold:
            if True:
                # if profitForSell(symbol, dictEvalSell, self.wallet) > 0:
                fromcurr = getFromCurrency(symbol)
                sellorder = self.ordermaker.makeOrder(symbol, dictEvalSell[symbol].price, Side.SELL,
                                                      self.wallet.amountForCurrency(fromcurr))
                if sellorder is not None:
                    print(dataDayEvaluation['datetime'].tail(1).values[0])
                    print(repr(sellorder))
                    sellOrders.append(sellorder)

        # buy by priority depending on proba
        sortByProba(buyablenow, dictEvalBuy)
        sortByProba(cannotbuy, dictEvalBuy)
        # for now, buy first what you can (we could optimize if proba cannotbuy much better. we would search what we can
        # sell in order to buy)
        for symbol in buyablenow:
            tocurr = getToCurrency(symbol)
            buyorder = self.ordermaker.makeOrder(symbol, dictEvalBuy[symbol].price, Side.BUY,
                                                 self.wallet.amountForCurrency(tocurr))
            if buyorder is not None:
                print(dataDayEvaluation['datetime'].tail(1).values[0])
                print(repr(buyorder))
                buyOrders.append(buyorder)

        return buyOrders, sellOrders

    def executeOrders(self):
        self.ordermaker.printOrders()
        self.ordermaker.executeOrders()
