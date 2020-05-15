from abc import ABC, abstractmethod
import pandas as pd

from binance.client import Client
import bitstamp.client
from stockstats import StockDataFrame
from tapy import Indicators

from indicators.MyAdx import ADXStrength
from indicators.adx import adx
from indicators.coppock import coppock
from indicators.psar import psar, sar
from ta.trend import ADXIndicator

from indicators.trueStrengthIndex import tsi


class DataRetriever(ABC):
    def __init__(self, symbolsBinance):
        self.clientBinance = Client('wCIy0XKixL1ykrcy0c2fXkjmk4ccnJ11Z5t7OiLiu5UFhASTINTNsPJz0iVvNFKa',
                                    'kVPKJc55SXotegHkNkyQoDIfMuhZTTAOOxmwTYt6XbCNBkaggan9OIwU6OpH2UzK')

        # 'https://api.binance.com/api/v3/klines'
        self.clientBitStamp = bitstamp.client.Public()
        self.symbolsBinance = symbolsBinance

    def retrieveAllDataWeekFor(self, startDateTime, endDateTime):
        return self.__retrieveAllDataFrom__(Client.KLINE_INTERVAL_1WEEK, startDateTime, endDateTime)

    def retrieveAllDataDayFor(self, startDateTime, endDateTime):
        return self.__retrieveAllDataFrom__(Client.KLINE_INTERVAL_1DAY, startDateTime, endDateTime)

    def __retrieveAllDataFrom__(self, interval, startDateTime, endDateTime):
        listdataframes = []
        for symbol in self.symbolsBinance:
            listdataframes.append(self.__historicDataFrameForSymbol__(interval, symbol, startDateTime, endDateTime))
        result = pd.concat(listdataframes)
        result.sort_index(inplace=True)
        return result

    def __historicDataFrameForSymbol__(self, interval, symbol, startDateTime, endDateTime):
        klines = self.clientBinance.get_historical_klines(symbol, interval, str(startDateTime), str(endDateTime), 1000)
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
        df["Close"] = pd.to_numeric(df["Close"], downcast="float")
        df["Open"] = pd.to_numeric(df["Open"], downcast="float")
        df["High"] = pd.to_numeric(df["High"], downcast="float")
        df["Low"] = pd.to_numeric(df["Low"], downcast="float")
        df['datetime'] = pd.to_datetime(df['opentime'], unit='ms')

        df.set_index('opentime', inplace=True)
        df.sort_index(inplace=True)  # sort by datetime
        df.reset_index(inplace=True)

        # calculate here some usefull indicators
        indicators = Indicators(df)
        indicators.awesome_oscillator()
        indicators.macd()
        indicators.momentum()

        df['macd_value'] = pd.to_numeric(indicators.df['macd_value'], downcast="float")
        df['macd_signal'] = pd.to_numeric(indicators.df['macd_signal'], downcast="float")
        df['macd_histo'] = df['macd_value'] - df['macd_signal']
        df['ao'] = indicators.df['ao']
        df['momentum'] = indicators.df['momentum']
        df['coppock'] = coppock(df["Close"])
        df['SAR'] = psar(df)

        # stock = StockDataFrame.retype(df.copy())
        adxI = ADXIndicator(df["High"], df["Low"], df["Close"], 14, False)
        df['pos_directional_indicator'] = adxI.adx_pos()
        df['neg_directional_indicator'] = adxI.adx_neg()
        df['adx'] = ADXStrength(df["High"], df["Low"], df["Close"])
        tupleTSI = tsi(df["Close"])
        df['tsi'] = tupleTSI[0]
        df['ematsi'] = tupleTSI[1]

        tsibefore = tupleTSI[0].shift(1)
        df['tauxtsi'] = 100*(tupleTSI[0] - tsibefore)/abs(tsibefore)

        df.set_index('opentime', inplace=True)
        # df.set_index('opentime', inplace=True)
        # df.reset_index(inplace=True)
        # df.set_index(["opentime", "symbol"], inplace=True)
        return df

    @abstractmethod
    def getCurrentPrice(self, symbol, opentime):
        return float(self.clientBinance.get_avg_price(symbol='BNBBTC')['price'])
