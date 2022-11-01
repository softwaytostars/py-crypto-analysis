from DataRetriever import DataRetriever
from Graphic import showAll
from algo.AlgoTrading import AlgoTrading
import pandas as pd


class BilanWallet:
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
            amount = wallet.amount_for_currency(curr)
            if curr == "USDT":
                totalEquivalentAmountUSDT += amount
            else:
                lastPriceInUsdt = dataDay['Close'].tail(1).values[0]
                totalEquivalentAmountUSDT += lastPriceInUsdt * amount
        return totalEquivalentAmountUSDT

    def ratio_after_before_usdt(self):
        orig_equivalent_amount_usdt = self.__equivalentUSDTForWallet__(self.walletorig, self.dataDayOrig)
        current_equivalent_amount_usdt = self.__equivalentUSDTForWallet__(self.endWallet, self.endDataDay)
        print("Amount USDT for %s : Before = % 5.7f , After = %5.7f, ratio = %5.7f" %
              (self.period,
               orig_equivalent_amount_usdt,
               current_equivalent_amount_usdt,
               current_equivalent_amount_usdt / orig_equivalent_amount_usdt))
        return current_equivalent_amount_usdt / orig_equivalent_amount_usdt


def show_data(data, name):
    # df = read_dataset("test.csv")
    # Dimensions of dataset
    # df.reset_index(inplace=True)
    # df = df.set_index('opentime')
    # df = df.sort_index()  # sort by datetime

    df2 = pd.DataFrame(data)
    df2 = df2.set_index('opentime')
    df2 = df2.sort_index()  # sort by datetime

    # alldf = pd.concat([df, df2], axis=1)
    showAll(df2, True, name)


def get_period_check(date, yearCheckWallets):
    for yearPeriod in yearCheckWallets:
        if date.startswith(yearPeriod):
            return yearPeriod
    return None


class Simulator(object):
    def __init__(self, all_symbols):
        self.allSymbols = all_symbols
        self.dataRetriever = DataRetriever(all_symbols)
        self.dataDayFrame = None
        self.dataWeekFrame = self.dataRetriever.retrieveAllDataWeekFor("01 Jan, 2019", None)

    def retrieveDataDayFrameIfNeeded(self, opentime):
        # si pas encore defini ou bien que le last index correspond à opentime
        if (self.dataDayFrame is None) or (self.dataDayFrame.index[-2] <= opentime):
            self.dataDayFrame = self.dataRetriever.retrieveAllDataDayFor(opentime, None)
        return self.dataDayFrame

    def run_simu(self, wallet):
        year_check_wallets = ['2020',
                              '2021',
                              '2022']
        dict_wallets_by_year = {}
        previous_period = None

        algo = AlgoTrading(self.allSymbols, wallet)

        result_day = {'opentime': [],
                      'datetime': [],
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
                      'tsi': [],
                      'ematsi': [],
                      'adx': []
                      }

        week_opentime_values = self.dataWeekFrame.index.get_level_values('opentime')
        interval_week = week_opentime_values[1] - week_opentime_values[0]

        self.retrieveDataDayFrameIfNeeded(week_opentime_values[0])
        last_data_for_day = None
        for last_week_opentime in week_opentime_values:
            self.retrieveDataDayFrameIfNeeded(last_week_opentime - 5 * interval_week)
            day_opentimevalues = self.dataDayFrame.loc[
                (self.dataDayFrame.index.get_level_values('opentime') >= last_week_opentime) &
                (self.dataDayFrame.index.get_level_values('opentime') < (
                        last_week_opentime + interval_week))].index.get_level_values(
                'opentime')
            for lastdayopentime in day_opentimevalues:
                if lastdayopentime < last_week_opentime:
                    continue
                dataForDay = self.dataDayFrame.loc[
                    self.dataDayFrame.index.get_level_values('opentime') == lastdayopentime]
                lastCloseprice = dataForDay['Close'].values[0]
                lastOpenprice = dataForDay['Open'].values[0]
                if self.dataWeekFrame.iloc[
                    (self.dataWeekFrame.index.get_level_values('opentime') == last_week_opentime)][
                    'ao'].isnull().values[0]:
                    result_day['opentime'].append(lastdayopentime)
                    result_day['datetime'].append(dataForDay['datetime'].values[0])
                    result_day['Close'].append(lastCloseprice)
                    result_day['Open'].append(lastOpenprice)
                    result_day['sell'].append(-100)
                    result_day['buy'].append(-100)
                    result_day['SAR'].append(-100)
                    result_day['ao'].append(-100)
                    result_day['macd_histo'].append(-100)
                    result_day['macd_value'].append(-100)
                    result_day['macd_signal'].append(-100)
                    result_day['tauxtsi'].append(-100)
                    result_day['tsi'].append(-100)
                    result_day['ematsi'].append(-100)
                    result_day['adx'].append(-100)
                    continue

                data_week_evaluation = self.dataWeekFrame.loc[
                    self.dataWeekFrame.index.get_level_values('opentime') <= last_week_opentime]

                # should be better but that slows down too much
                # data_week_evaluation = self.dataWeekFrame.loc[
                #     (self.dataWeekFrame.index.get_level_values('opentime') <= last_week_opentime) &
                #     (self.dataWeekFrame.index.get_level_values('opentime') > last_week_opentime-10*interval_week)]

                # strictly because we will make decision from previous day
                data_day_evaluation = self.dataDayFrame.loc[
                    self.dataDayFrame.index.get_level_values('opentime') < lastdayopentime]

                currentDayData = self.dataDayFrame.loc[
                    self.dataDayFrame.index.get_level_values('opentime') == lastdayopentime]
                current_price = currentDayData['Open'].tail(1).values[0]
                currendDate = str(currentDayData['datetime'].tail(1).values[0])

                period = get_period_check(currendDate, year_check_wallets)
                if period is not None and (previous_period is None or period != previous_period):
                    dict_wallets_by_year[period] = BilanWallet(period, wallet.copy(), data_day_evaluation.copy())
                    if previous_period is not None:
                        dict_wallets_by_year.get(previous_period).setEndWallet(wallet.copy(),
                                                                               data_day_evaluation.copy())
                    previous_period = period
                last_data_for_day = data_day_evaluation.copy()

                # algo tells what to buy and sell
                (buyOrders, sellOrders) = algo.compute(data_week_evaluation, data_day_evaluation, current_price,
                                                       currendDate)

                result_day['opentime'].append(lastdayopentime)
                result_day['datetime'].append(dataForDay['datetime'].values[0])
                result_day['Close'].append(lastCloseprice)
                result_day['Open'].append(lastOpenprice)
                result_day['SAR'].append(dataForDay['SAR'].values[0])
                result_day['ao'].append(dataForDay['ao'].values[0])
                result_day['macd_histo'].append(dataForDay['macd_histo'].values[0])
                result_day['macd_value'].append(dataForDay['macd_value'].values[0])
                result_day['macd_signal'].append(dataForDay['macd_signal'].values[0])
                result_day['tauxtsi'].append(dataForDay['tauxtsi'].values[0])
                result_day['tsi'].append(dataForDay['tsi'].values[0])
                result_day['ematsi'].append(dataForDay['ematsi'].values[0])
                result_day['adx'].append(dataForDay['adx'].values[0])
                if len(buyOrders) >= 1:
                    result_day['buy'].append(buyOrders[0].getPrice())
                else:
                    result_day['buy'].append(0)
                if len(sellOrders) >= 1:
                    result_day['sell'].append(sellOrders[0].getPrice())
                else:
                    result_day['sell'].append(0)

                algo.execute_orders()

        # if last period
        if previous_period == year_check_wallets[len(year_check_wallets) - 1]:
            dict_wallets_by_year.get(previous_period).setEndWallet(wallet.copy(), last_data_for_day)

        result = []
        for period in dict_wallets_by_year.keys():
            result.append(dict_wallets_by_year.get(period).ratio_after_before_usdt())

        show_data(result_day, "day.html")
        # show_data(result_week, "week.html")
        return result
