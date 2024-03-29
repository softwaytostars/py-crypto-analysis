from abc import ABC, abstractmethod

import pandas as pd

from binance.client import Client
from tapy import Indicators

from Utils import load_properties_from_file
from indicators.adx import adx, average_directional_movement_index
from indicators.coppock import coppock
from indicators.psar import psar, sar
from ta.trend import ADXIndicator

from indicators.trueStrengthIndex import tsi


def __convert_to_str__(date):
    return None if date is None else str(date)

class DataRetriever(ABC):
    def __init__(self, symbolsBinance):
        props = load_properties_from_file('credentials.properties')
        self.clientBinance = Client(props['BINANCE_API_KEY'],
                                    props['BINANCE_API_SECRET'])
        self.symbolsBinance = symbolsBinance

    def retrieveAllDataWeekFor(self, startDateTime, endDateTime):
        return self.__retrieveAllDataFrom__(Client.KLINE_INTERVAL_1WEEK, startDateTime, endDateTime)

    def retrieveAllDataDayFor(self, startDateTime, endDateTime):
        return self.__retrieveAllDataFrom__(Client.KLINE_INTERVAL_1DAY, startDateTime, endDateTime)

    def __retrieveAllDataFrom__(self, interval, startDateTime, endDateTime):
        listdataframes = []
        for symbol in self.symbolsBinance:
            listdataframes.append(self.__historicDataFrameForSymbol__(interval,
                                                                      symbol,
                                                                      __convert_to_str__(startDateTime),
                                                                      __convert_to_str__(endDateTime)))
        result = pd.concat(listdataframes)
        result.sort_index(inplace=True)
        return result

    def __historicDataFrameForSymbol__(self, interval, symbol, startDateTime, endDateTime):
        klines = self.clientBinance.get_historical_klines(symbol, interval, startDateTime, endDateTime, 1000)
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
        indicators.bollinger_bands()

        df['macd_value'] = pd.to_numeric(indicators.df['macd_value'], downcast="float")
        df['macd_signal'] = pd.to_numeric(indicators.df['macd_signal'], downcast="float")
        df['macd_histo'] = df['macd_value'] - df['macd_signal']
        df['ao'] = indicators.df['ao']
        df['momentum'] = indicators.df['momentum']
        df['coppock'] = coppock(df["Close"])
        df['SAR'] = psar(df)
        df['bollinger_top'] = indicators.df['bollinger_top']
        df['bollinger_bottom'] = indicators.df['bollinger_bottom']
        df['bollinger_mid'] = indicators.df['bollinger_mid']

        # stock = StockDataFrame.retype(df.copy())
        adxI = ADXIndicator(df["High"], df["Low"], df["Close"], 14, False)
        df['pos_directional_indicator'] = adxI.adx_pos()
        df['neg_directional_indicator'] = adxI.adx_neg()
        df['adx'] = average_directional_movement_index(df.copy(), 14, 14)
        tupleTSI = tsi(df["Close"])
        df['tsi'] = tupleTSI[0]
        df['ematsi'] = tupleTSI[1]

        tsibefore = tupleTSI[0].shift(1)
        df['tauxtsi'] = 100 * (tupleTSI[0] - tsibefore) / abs(tsibefore)

        df.set_index('opentime', inplace=True)

        df.to_csv(symbol + ".csv", index=True)

        # df.set_index('opentime', inplace=True)
        # df.reset_index(inplace=True)
        # df.set_index(["opentime", "symbol"], inplace=True)
        return df

    def get_current_price(self, symbol, opentime):
        return float(self.clientBinance.get_avg_price(symbol=symbol)['price'])
