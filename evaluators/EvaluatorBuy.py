import math

from evaluators.Evaluation import Evaluation
from evaluators.Evaluator import Evaluator


class EvaluatorBuy(Evaluator):
    def __init__(self, dataWeekEvaluation, dataDayEvaluation, currentPrice):
        super().__init__(dataWeekEvaluation, dataDayEvaluation, currentPrice)

    def firstVersion(self, dataWeekEvaluation, dataDayEvaluation, currentPrice):
        previoushisto = dataWeekEvaluation['macd_histo'].tail(2).values[0]
        currentMacdhisto = dataWeekEvaluation['macd_histo'].tail(1).values[0]
        evaluation = Evaluation(0, currentPrice)
        penteSignal = dataWeekEvaluation['macd_signal'].tail(1).values[0] - \
                      dataWeekEvaluation['macd_signal'].tail(2).values[0]
        penteMacd = dataWeekEvaluation['macd_value'].tail(1).values[0] - \
                    dataWeekEvaluation['macd_value'].tail(2).values[0]
        rapportPente = abs(penteMacd / penteSignal)
        # and rapportPente >= 15
        if penteMacd > 0 and currentMacdhisto > 0 and previoushisto <= 0 and rapportPente > 1:
            evaluation = Evaluation(1, currentPrice)
        return evaluation

    def evaluate(self, dataWeekEvaluation, dataDayEvaluation, currentPrice):
        lastAOweek = dataWeekEvaluation['ao'].tail(1).values[0]
        previousAOweek = dataWeekEvaluation['ao'].tail(2).values[0]
        lastSARweek = dataWeekEvaluation['SAR'].tail(1).values[0]
        lastMacdHistoWeek = dataWeekEvaluation['macd_histo'].tail(1).values[0]
        previousMacdHistoWeek = dataWeekEvaluation['macd_histo'].tail(2).values[0]
        lastMacdHistoDay = dataDayEvaluation['macd_histo'].tail(1).values[0]
        previousMacdHistoDay = dataDayEvaluation['macd_histo'].tail(2).values[0]
        weekmacdincrease = lastMacdHistoWeek >= previousMacdHistoWeek and lastMacdHistoWeek >= 0
        lastSARday = dataDayEvaluation['SAR'].tail(1).values[0]
        # Bullish scenario long term
        if currentPrice > lastSARweek and weekmacdincrease:
            if lastAOweek <= 0 and previousAOweek < 0 and lastAOweek > previousAOweek and currentPrice > lastSARday:

                lastAOday = dataDayEvaluation['ao'].tail(1).values[0]
                previousAOday = dataDayEvaluation['ao'].tail(2).values[0]
                if lastAOday > previousAOday and lastAOday > 0:
                    return Evaluation(1, currentPrice)
        # Bearish scenario long term
        if currentPrice <= lastSARweek:
            previousSARweek = dataWeekEvaluation['SAR'].tail(2).values[0]
            lastAOday = dataDayEvaluation['ao'].tail(1).values[0]
            previousAOday = dataDayEvaluation['ao'].tail(2).values[0]
            if lastAOweek < 0 and lastMacdHistoWeek > previousMacdHistoWeek and lastAOday <= 0 and lastAOday > previousAOday:
                # bulish day
                if currentPrice > lastSARday:
                    return Evaluation(1, currentPrice)
            # bearsih long term but bullish short term
            if currentPrice > lastSARday:
                if lastMacdHistoDay >= 0 and lastMacdHistoDay > previousMacdHistoDay:
                    if lastAOday < 0 and lastAOday > previousAOday:
                        # compter le nbre de jours que le prix est en sar bullsih day (si super à 2 jours, on laisse tomber)
                        if self.stillAGoodBuyBullishDayInBearishWeek(dataDayEvaluation, currentPrice):
                            return Evaluation(1, currentPrice)

        return Evaluation(0, currentPrice)

    def stillAGoodBuyBullishDayInBearishWeek(self, dataDayEvaluation, currentPrice):
        n = 0
        for i in range(1, 4):
            sarDay = dataDayEvaluation['SAR'].tail(i).values[0]
            if currentPrice > sarDay:
                n + 1
        return 0 < n <= 2;

    def evaluateBuy(self):

        if str(self.dataDayEvaluation['datetime'].tail(1).values[0]) == "2020-01-06T00:00:00.000000000":
            print('debug')

        if self.getStrengthADX(0) < 15:
            return Evaluation(0, self.currentPrice)

        # if not self.isTauxStrengthDayEnought(0) :
        #     return Evaluation(0, self.currentPrice)


        # si on entre toute juste en bullish week growing, faut acheter
        if self.isGrowingBullishWeek(0) and not self.isGrowingBullishWeek(1):
            return Evaluation(1, self.currentPrice)
        # if on est en bearish week mais qu'on entre en bullish day, faut acheter
        if not self.isBullishWeek(0) and self.isWorthToBuyInBearishWeek(0) \
                and self.isGrowingBullishDay(0) and self.isBullishDayOrFarFromBeginBearishDay(0):
            return Evaluation(1, self.currentPrice)
        return Evaluation(0, self.currentPrice)

