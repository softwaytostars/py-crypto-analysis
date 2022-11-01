from evaluators.Evaluation import Evaluation
from evaluators.TradingToolCalculator import TradingToolCalculator


class EvaluatorSell(TradingToolCalculator):
    def __init__(self, data_week_evaluation, data_day_evaluation, current_price):
        super().__init__(data_week_evaluation, data_day_evaluation, current_price)

    def evaluate(self, data_week_evaluation, data_day_evaluation, current_price):
        lastAOweek = data_week_evaluation['ao'].tail(1).values[0]
        previousAOweek = data_week_evaluation['ao'].tail(2).values[0]
        lastSARweek = data_week_evaluation['SAR'].tail(1).values[0]
        lastAOday = data_day_evaluation['ao'].tail(1).values[0]
        previousAOday = data_day_evaluation['ao'].tail(2).values[0]
        lastSARday = data_day_evaluation['SAR'].tail(1).values[0]
        lastMacdHistoWeek = data_week_evaluation['macd_histo'].tail(1).values[0]
        previousMacdHistoWeek = data_week_evaluation['macd_histo'].tail(2).values[0]
        lastMacdHistoDay = data_day_evaluation['macd_histo'].tail(1).values[0]
        previousMacdHistoDay = data_day_evaluation['macd_histo'].tail(2).values[0]

        isBigBullishWeek = current_price > lastSARweek and lastAOweek > previousAOweek and lastMacdHistoWeek > 0 and lastMacdHistoWeek > previousMacdHistoWeek
        isStillBullishWeek = current_price > lastSARweek and lastMacdHistoWeek > 0 and lastAOweek > previousAOweek
        if isBigBullishWeek or isStillBullishWeek:
            if current_price < lastSARday and lastAOday < previousAOday and lastAOday <= 0 and lastMacdHistoDay < previousMacdHistoDay:
                return Evaluation(1, current_price)
            else:
                return Evaluation(0, current_price)
        if lastAOweek > 0:
            if lastAOday > 0 and lastAOday < previousAOday:
                return Evaluation(1, current_price)
        # elif lastAOweek <= 0 and lastAOweek >= previousAOweek:
        #     weekmacdincrease = lastMacdHistoWeek > previousMacdHistoWeek and lastMacdHistoWeek > 0
        #     daymacddecrease = lastMacdHistoDay < previousMacdHistoDay and lastMacdHistoDay > 0
        #     if not weekmacdincrease and daymacddecrease:
        #         return Evaluation(1, current_price)
        elif lastAOweek <= 0:
            weekmacdincrease = lastMacdHistoWeek > previousMacdHistoWeek and lastMacdHistoWeek > 0
            daymacddecrease = lastMacdHistoDay < previousMacdHistoDay and lastMacdHistoDay > 0
            if not weekmacdincrease and daymacddecrease and lastAOday < previousAOday:
                return Evaluation(1, current_price)
        return Evaluation(0, current_price)

    def priceCannotGrowMoreInDay(self):
        return self.priceCanGrowInDay(1) and not self.priceCanGrowInDay(0)

    def evaluateSell(self):
        if str(self.data_day_evaluation['datetime'].tail(1).values[0]) == "2018-07-16T00:00:00.000000000":
            print('debug')
        #tsi est negatif, pas la peine de considerer la vente
        if self.getTSIWeek(0) < -3:
            return Evaluation(0, self.current_price)

        if self.isBullishWeek(0):
            # si en bullish week, on vend seulement si plus growing bullish (ameriorer en utilisant momentum week)
            if self.isGrowingBullishWeek(1) and not self.isGrowingBullishWeek(0):
                return Evaluation(1, self.current_price)
            # elif self.priceCannotGrowMoreInDay():
            #     return Evaluation(1, self.current_price)
            else:
                return Evaluation(0, self.current_price)
        else:
            # si on etait en bullish week la semaine d'avant alors on vend
            if self.isBullishWeek(1):
                return Evaluation(1, self.current_price)
            # si on est en bearish week et qu'on a de la currency, il faut vendre dès qu'on est plus en bullish day
            if self.priceCannotGrowMoreInDay():
                return Evaluation(1, self.current_price)

        return Evaluation(0.5, self.current_price)

