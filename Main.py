import datetime
import copy
import json
from tapy import Indicators
from collections import namedtuple

from binance.client import Client
import pandas as pd
from stockstats import StockDataFrame

from Graphic import showAll
from Model import Side
from OrderMaker import OrderMaker
from SimulationDataRetriever import SimulationDataRetriever
from Utils import getFromToCurrencies, sortByProba, sortByProfit, getToCurrency, getFromCurrency, profitForSell
from Wallet import Wallet
from evaluators.EvaluatorBuy import EvaluatorBuy
from evaluators.EvaluatorSell import EvaluatorSell


def test2():
    client = Client('wCIy0XKixL1ykrcy0c2fXkjmk4ccnJ11Z5t7OiLiu5UFhASTINTNsPJz0iVvNFKa',
                    'kVPKJc55SXotegHkNkyQoDIfMuhZTTAOOxmwTYt6XbCNBkaggan9OIwU6OpH2UzK')

    # get market depth
    # depth = client.get_order_book(symbol='BNBBTC')

    # try:
    #     order = client.create_test_order(
    #         symbol='BNBBTC',
    #         side=Client.SIDE_BUY,
    #         type=Client.ORDER_TYPE_LIMIT,
    #         quantity=100)
    # except Exception as e:
    #     print(e)

    # get all symbol prices
    # prices = client.get_all_tickers()
    avg_price = client.get_avg_price(symbol='BNBBTC')
    x = json.loads(avg_price, object_hook=lambda d: namedtuple('X', d.keys())(*d.values()))
    client.get_account()['balances']  # asset free, locked

    # fetch 1 minute klines for the last day up until now
    # klines = client.get_historical_klines("BNBBTC", Client.KLINE_INTERVAL_1MINUTE, "1 day ago UTC")

    # fetch 30 minute klines for the last month of 2017
    # klines = client.get_historical_klines("ETHBTC", Client.KLINE_INTERVAL_30MINUTE, "1 Dec, 2017", "1 Jan, 2018")

    # https://github.com/binance-exchange/binance-official-api-docs/blob/master/rest-api.md#24hr-ticker-price-change-statistics
    # fetch weekly klines since it listed

    klines = client.get_historical_klines("NEOBTC", Client.KLINE_INTERVAL_1WEEK, "1 Jan, 2017")

    df = pd.DataFrame(klines)
    df.columns = ["opentime", "Open", "High", "Low", "Close", "volume", "closeTime", "quoteAssetVolume", "numberTrades",
                  "takerBuyBaseAssetVolume", "takerBuyQuoteAssetVolume", 'ignore']
    # df['opentime'] = pd.to_datetime(df['opentime'], unit='ms')
    df.to_csv("test.csv", index=False)


def read_dataset(filename):
    print('Reading data from %s' % filename)
    df = pd.read_csv(filename)
    df = df.set_index('opentime')
    df = df.sort_index()  # sort by datetime
    print(df.shape)
    return df


def read_datasetBitStamp(filename):
    print('Reading data from %s' % filename)
    df = pd.read_csv(filename)
    df = df.set_index('opentime')
    df = df.sort_index()  # sort by datetime
    print(df.shape)
    return df


def test(df, dictBuySell):
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


def historicDataFrameForSymbol(symbol):
    klines = client.get_historical_klines(symbol, Client.KLINE_INTERVAL_1WEEK, "1 Jan, 2017")
    df = pd.DataFrame(klines)
    df.columns = ["opentime",
                  "Open",
                  "High",
                  "Low",
                  "Close",
                  "volume",
                  "closetime",
                  "quoteassetVolume",
                  "numbertrades",
                  "takerbuybaseassetvolume",
                  "takerbuyquoteassetvolume",
                  "ignore"]
    df['symbol'] = symbol
    df.set_index(["opentime", "symbol"], inplace=True)

    return df


def getDataForEvaluation(allDataFrame, intervalTime, opentime, symbol, nPeriodsForEvaluation):
    # look for the first opentime available for the symbol
    firstopentime = \
        allDataFrame.loc[(allDataFrame.index.get_level_values('symbol') == symbol)].index.get_level_values('opentime')[
            0]
    startopentime = max(firstopentime, opentime - nPeriodsForEvaluation * intervalTime)
    dataOld = allDataFrame.loc[
        # (allDataFrame.index.get_level_values('opentime') >= startopentime) &
        (allDataFrame.index.get_level_values('opentime') <= opentime) &
        (allDataFrame.index.get_level_values('symbol') == symbol)]

    stock = dataOld.copy()
    fast_ma = stock['Close'].ewm(span=12,min_periods=0,adjust=False,ignore_na=False).mean()
    slow_ma = stock['Close'].ewm(span=26,min_periods=0,adjust=False,ignore_na=False).mean()
    macd = fast_ma - slow_ma
    signal = macd.ewm(span=9,min_periods=0,adjust=False,ignore_na=False).mean()
    stock['macd'] = macd
    stock['macdh'] = macd - signal
    stock['macds'] = signal

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
    return stock


# for NN
def checkExpectedResult(currentindex, dataframe, evaluation):
    nextrows = dataframe.iloc[currentindex + 1: currentindex + nperiodLaterCheck + 1]
    # si dans la periode consideree, le prix a augmente d'au moins 10%, on est bon si on a achete, sinon on est mauvaus
    # si on a vendu , il faut que le prix n'ait pas monté de 10% sinon on est pas bon
    highest = 0
    for index, nextrow in nextrows.iterrows():
        highest = max(highest, nextrow.High)

    diff = (highest - evaluation.price) / evaluation.price
    if evaluation.side == Side.BUY:
        if diff >= 10 / 100:
            return 1;
        elif diff > 0:
            return 0.5
        else:
            return 0
    elif evaluation.side == Side.SELL:
        if diff >= 10 / 100:
            return 0
        elif diff <= -10 / 100:
            return 1
        else:
            return 0.5
    else:
        if diff >= 10 / 100:
            return 0
        elif diff <= -10 / 100:
            return 1
        else:
            return 0.5;


nperiodLaterCheck = 4


def evaluationData(symbol, dataframe, decisionmaker, currentAvgPrice):
    # demarre pas de suite car i faut des periodes historiques pour la data pour evaluation indicators
    for i in range(nPeriodsForEvaluation, dataframe.shape[0] - nperiodLaterCheck):
        dataForEvaluation = getDataForEvaluation(i, dataframe)
        # evaluation doit contenir (BUY,SELL, or nothing + limit order price)
        # currentPrice = getCurrentPrice(i, dataframe)
        # evaluationBuy = evaluatorBuy.evaluate(dataForEvaluation, currentPrice)
        # evaluationSell = evaluatorSell.evaluate(dataForEvaluation, currentPrice)
        # # make decision
        # if evaluationBuy > 0.7:


# todo gerer si ordres encore en cours
wallet = Wallet()
wallet.addToWalletWithoutOrigin('USDT', 1)
# wallet.addToWalletWithoutOrigin('BTC', 1)

walletorig = wallet.copy()

dictBuySellOrders = {'opentime': [],
                     'buy': [],
                     'sell': []
                     }

walletorig = copy.deepcopy(wallet)
print('wallorigin')
print(walletorig)

ordermaker = OrderMaker(wallet)

allSymbolsInBinance = ["BTCUSDT"]
allSymbolsInBitstamp = []
dataRetriever = SimulationDataRetriever(allSymbolsInBinance, allSymbolsInBitstamp)
dataRetriever.retrieveAllDataWeekFrom("1 Jan, 2015")

allSymbols = allSymbolsInBinance
allSymbols.extend(allSymbolsInBitstamp)

evaluatorBuy = EvaluatorBuy()
evaluatorSell = EvaluatorSell()
# listdataframes = []
# for symbol in allSymbols:
#     listdataframes.append(historicDataFrameForSymbol(symbol))
#
# allDataFrame = pd.concat(listdataframes)
# allDataFrame.sort_index(inplace=True)

opentimevalues = dataRetriever.allDataFrame.index.get_level_values('opentime')
intervalTime = opentimevalues[1] - opentimevalues[0]
nPeriodsForEvaluation = 22  # parametre à optimiser
startSimu = 3
start = 0
for opentime in opentimevalues:
    start += 1
    if start <= startSimu:
        dictBuySellOrders['opentime'].append(opentime)
        dictBuySellOrders['sell'].append(0)
        dictBuySellOrders['buy'].append(0)
        continue
    dictEvalBuy = {}
    dictEvalSell = {}
    buyablenow = []
    cannotbuy = []
    willbesold = []

    dictCurrentPrice = {}
    # determine evaluation buy/sell for reach symbol
    for symbol in allSymbols:
        currentPrice = dataRetriever.getCurrentPrice(symbol, opentime)
        dictCurrentPrice[symbol] = currentPrice
        dataForEvaluation = getDataForEvaluation(dataRetriever.allDataFrame, intervalTime, opentime, symbol,
                                                 nPeriodsForEvaluation)
        dictEvalBuy[symbol] = evaluatorBuy.evaluate(dataForEvaluation, currentPrice)
        dictEvalSell[symbol] = evaluatorSell.evaluate(dataForEvaluation, currentPrice)
        # what can we buy ?
        (fromcurr, tocurr) = getFromToCurrencies(symbol)
        # should sell if probability is greater than 70% (# parametre à optimiser)
        shouldBeSold = dictEvalSell.get(symbol).proba > 0.70
        # should buy if probability is greater than (# parametre à optimiser)
        shouldBeBought = dictEvalBuy.get(symbol).proba > 0.60
        # on veut revendre dans la même currency d'achat à moins que ce soit pour acheter quelque chose qu'on ne peut
        # pas avoir mais ca sera plus + tard (cf gestion cannotbuy)
        # and currentStock.get(fromcurr).frompairorigin == symbol
        if shouldBeSold and wallet.amountForCurrency(fromcurr) > 0:
            willbesold.append(symbol)
        if shouldBeBought:
            if wallet.amountForCurrency(tocurr) > 0:
                buyablenow.append(symbol)
            else:
                cannotbuy.append(symbol)

    # put orders (priority to sell orders to make profit now) on veut revendre dans la même currency d'achat à moins
    # que ce soit pour acheter quelque chose qu'on ne peut pas avoir mais ca sera plus + tard (cf gestion )cannotbuy
    sortByProfit(willbesold, dictEvalSell, wallet)
    valsell = 0
    for symbol in willbesold:
        if profitForSell(symbol, dictEvalSell, wallet) > 0:
            fromcurr = getFromCurrency(symbol)
            ordermaker.makeOrder(symbol, dictEvalSell[symbol].price, Side.SELL, wallet.amountForCurrency(fromcurr))
            valsell = dictEvalSell[symbol].price
    # buy by priority depending on proba
    sortByProba(buyablenow, dictEvalBuy)
    sortByProba(cannotbuy, dictEvalBuy)
    # for now, buy first what you can (we could optimize if proba cannotbuy much better. we would search what we can
    # sell in order to buy)
    valbuy = 0
    for symbol in buyablenow:
        tocurr = getToCurrency(symbol)
        ordermaker.makeOrder(symbol, dictEvalBuy[symbol].price, Side.BUY, wallet.amountForCurrency(tocurr))
        valbuy = dictEvalBuy[symbol].price

    dictBuySellOrders['opentime'].append(opentime)
    dictBuySellOrders['sell'].append(valsell)
    dictBuySellOrders['buy'].append(valbuy)


    # print(datetime.datetime.fromtimestamp(opentime).isoformat())
    print(opentime)
    ordermaker.printOrders()
    ordermaker.executeOrders()
    print('wallet :')
    print(wallet)

# Bilan:
for curr in (set(walletorig.currentStock.keys()) & set(wallet.currentStock.keys())):
    amountorig = walletorig.amountForCurrency(curr)
    currentamount = wallet.amountForCurrency(curr)
    print("currency : % s, Before : % 5.7f, After : % 5.7f, Diff % 2.2f " % (
        curr, amountorig, currentamount, 100 * (currentamount - amountorig) / amountorig))

test(dataRetriever.allDataFrame, dictBuySellOrders)
# df = dataRetriever.evaluationDataForSymbol(symbol)

# currentAvgPrice = dataRetriever.currentPrice(symbol)
# evaluationBySymbol[symbol] = decisionmaker.evaluate(df, currentAvgPrice)
# evaluationBySymbol = evaluationData(df, decisionmaker)

# decision en fonction des evaluations et du currentstock
