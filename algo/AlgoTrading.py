from tapy import Indicators

from Model import Side
from OrderMaker import OrderMaker
from Utils import getFromToCurrencies, sortByProfit, profitForSell, getFromCurrency, sortByProba, getToCurrency
from evaluators.EvaluatorBuy import EvaluatorBuy
from evaluators.EvaluatorHandler import EvaluatorHandler
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
        self.evaluatorHandler = EvaluatorHandler()

    def compute(self, dataWeekEvaluation, dataDayEvaluation, currentPrice, strCurrentDate):
        self.evaluatorHandler.initWithData(dataWeekEvaluation, dataDayEvaluation, currentPrice)

        if strCurrentDate == "2019-08-02T00:00:00.000000000":
            print('debug')

        sellOrders = []
        buyOrders = []

        dictEvalBuy = {}
        dictEvalSell = {}
        buyablenow = []
        cannotbuy = []
        willbesold = []

        # determine evaluation buy/sell for reach symbol
        for symbol in self.allSymbols:
            dictEvalBuy[symbol] = self.evaluatorHandler.evaluateBuy()
            dictEvalSell[symbol] = self.evaluatorHandler.evaluateSell()
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
                    print(strCurrentDate)
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
                print(strCurrentDate)
                print(repr(buyorder))
                buyOrders.append(buyorder)

        return buyOrders, sellOrders

    def executeOrders(self):
        self.ordermaker.printOrders()
        self.ordermaker.executeOrders()
