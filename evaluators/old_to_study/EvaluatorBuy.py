import math

from evaluators.Evaluation import Evaluation
from evaluators.TradingToolCalculator import TradingToolCalculator


class EvaluatorBuy(TradingToolCalculator):
    def __init__(self, data_week_evaluation, data_day_evaluation, current_price):
        super().__init__(data_week_evaluation, data_day_evaluation, current_price)

    def evaluate(self, data_week_evaluation, data_day_evaluation, current_price):
        lastAOweek = data_week_evaluation['ao'].tail(1).values[0]
        previousAOweek = data_week_evaluation['ao'].tail(2).values[0]
        lastSARweek = data_week_evaluation['SAR'].tail(1).values[0]
        lastMacdHistoWeek = data_week_evaluation['macd_histo'].tail(1).values[0]
        previousMacdHistoWeek = data_week_evaluation['macd_histo'].tail(2).values[0]
        lastMacdHistoDay = data_day_evaluation['macd_histo'].tail(1).values[0]
        previousMacdHistoDay = data_day_evaluation['macd_histo'].tail(2).values[0]
        weekmacdincrease = lastMacdHistoWeek >= previousMacdHistoWeek and lastMacdHistoWeek >= 0
        lastSARday = data_day_evaluation['SAR'].tail(1).values[0]
        # Bullish scenario long term
        if current_price > lastSARweek and weekmacdincrease:
            if 0 >= lastAOweek > previousAOweek and previousAOweek < 0 and current_price > lastSARday:

                lastAOday = data_day_evaluation['ao'].tail(1).values[0]
                previousAOday = data_day_evaluation['ao'].tail(2).values[0]
                if lastAOday > previousAOday and lastAOday > 0:
                    return Evaluation(1, current_price)
        # Bearish scenario long term
        if current_price <= lastSARweek:
            lastAOday = data_day_evaluation['ao'].tail(1).values[0]
            previousAOday = data_day_evaluation['ao'].tail(2).values[0]
            if lastAOweek < 0 and lastMacdHistoWeek > previousMacdHistoWeek and lastAOday <= 0 and lastAOday > previousAOday:
                # bulish day
                if current_price > lastSARday:
                    return Evaluation(1, current_price)
            # bearish long term but bullish short term
            if current_price > lastSARday:
                if lastMacdHistoDay >= 0 and lastMacdHistoDay > previousMacdHistoDay:
                    if lastAOday < 0 and lastAOday > previousAOday:
                        # compter le nbre de jours que le prix est en sar bullsih day (si super à 2 jours, on laisse tomber)
                        if self.stillAGoodBuyBullishDayInBearishWeek(data_day_evaluation, current_price):
                            return Evaluation(1, current_price)

        return Evaluation(0, current_price)

    def stillAGoodBuyBullishDayInBearishWeek(self, data_day_evaluation, current_price):
        n = 0
        for i in range(1, 4):
            sarDay = data_day_evaluation['SAR'].tail(i).values[0]
            if current_price > sarDay:
                n + 1
        return 0 < n <= 2;

    def evaluateBuy(self):

        if str(self.data_day_evaluation['datetime'].tail(1).values[0]) == "2018-04-12T00:00:00.000000000":
            print('debug')
        if str(self.data_day_evaluation['datetime'].tail(1).values[0]) == "2018-04-13T00:00:00.000000000":
            print('debug')
        if str(self.data_day_evaluation['datetime'].tail(1).values[0]) == "2018-02-13T00:00:00.000000000":
            print('debug')

        if self.getDMIADXWeek(0) < 15:
            return Evaluation(0, self.current_price)

        # if not self.isTauxStrengthDayEnought(0) :
        #     return Evaluation(0, self.current_price)

        # si on entre toute juste en bullish week growing, faut acheter
        if self.isGrowingBullishWeek(0) and not self.isGrowingBullishWeek(1):
            return Evaluation(1, self.current_price)
        # if self.isBullishWeek(0) and self.isBecomingTrueStrengthBullishDayUnderBullishWeek(0):
        #     return Evaluation(1, self.current_price)

        # if on est en bearish week mais qu'on entre en bullish day, faut acheter
        if not self.isBullishWeek(0)  and self.isGrowingBullishDay(0):
            return Evaluation(1, self.current_price)
        return Evaluation(0, self.current_price)
