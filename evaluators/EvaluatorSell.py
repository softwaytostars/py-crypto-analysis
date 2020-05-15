from evaluators.Evaluation import Evaluation
from evaluators.Evaluator import Evaluator


class EvaluatorSell(Evaluator):
    def __init__(self, dataWeekEvaluation, dataDayEvaluation, currentPrice):
        super().__init__(dataWeekEvaluation, dataDayEvaluation, currentPrice)

    # todo seulement si pente histo negative et pourcentage baisse > ? et
    def firstversion(self, dataWeekEvaluation, dataDayEvaluation, currentPrice):
        currentMacd = dataWeekEvaluation['macd_value'].tail(1).values[0]
        previousMacd = dataWeekEvaluation['macd_value'].tail(2).values[0]
        penteMacd = currentMacd - previousMacd
        currentMacdhisto = dataWeekEvaluation['macd_histo'].tail(1).values[0]

        previoushisto = dataWeekEvaluation['macd_histo'].tail(2).values[0]
        evaluation = Evaluation(0, currentPrice)
        penteHisto = (currentMacdhisto - previoushisto)
        rapport = abs(penteHisto / previoushisto) * 100
        if penteHisto <= 0 and previoushisto > 0 and rapport >= 20:
            evaluation = Evaluation(1, currentPrice)
        return evaluation

    def evaluate(self, dataWeekEvaluation, dataDayEvaluation, currentPrice):
        lastAOweek = dataWeekEvaluation['ao'].tail(1).values[0]
        previousAOweek = dataWeekEvaluation['ao'].tail(2).values[0]
        lastSARweek = dataWeekEvaluation['SAR'].tail(1).values[0]
        lastAOday = dataDayEvaluation['ao'].tail(1).values[0]
        previousAOday = dataDayEvaluation['ao'].tail(2).values[0]
        lastSARday = dataDayEvaluation['SAR'].tail(1).values[0]
        lastMacdHistoWeek = dataWeekEvaluation['macd_histo'].tail(1).values[0]
        previousMacdHistoWeek = dataWeekEvaluation['macd_histo'].tail(2).values[0]
        lastMacdHistoDay = dataDayEvaluation['macd_histo'].tail(1).values[0]
        previousMacdHistoDay = dataDayEvaluation['macd_histo'].tail(2).values[0]

        isBigBullishWeek = currentPrice > lastSARweek and lastAOweek > previousAOweek and lastMacdHistoWeek > 0 and lastMacdHistoWeek > previousMacdHistoWeek
        isStillBullishWeek = currentPrice > lastSARweek and lastMacdHistoWeek > 0 and lastAOweek > previousAOweek
        if isBigBullishWeek or isStillBullishWeek:
            if currentPrice < lastSARday and lastAOday < previousAOday and lastAOday <= 0 and lastMacdHistoDay < previousMacdHistoDay:
                return Evaluation(1, currentPrice)
            else:
                return Evaluation(0, currentPrice)
        if lastAOweek > 0:
            if lastAOday > 0 and lastAOday < previousAOday:
                return Evaluation(1, currentPrice)
        # elif lastAOweek <= 0 and lastAOweek >= previousAOweek:
        #     weekmacdincrease = lastMacdHistoWeek > previousMacdHistoWeek and lastMacdHistoWeek > 0
        #     daymacddecrease = lastMacdHistoDay < previousMacdHistoDay and lastMacdHistoDay > 0
        #     if not weekmacdincrease and daymacddecrease:
        #         return Evaluation(1, currentPrice)
        elif lastAOweek <= 0:
            weekmacdincrease = lastMacdHistoWeek > previousMacdHistoWeek and lastMacdHistoWeek > 0
            daymacddecrease = lastMacdHistoDay < previousMacdHistoDay and lastMacdHistoDay > 0
            if not weekmacdincrease and daymacddecrease and lastAOday < previousAOday:
                return Evaluation(1, currentPrice)
        return Evaluation(0, currentPrice)

    def evaluateSell(self):
        if str(self.dataDayEvaluation['datetime'].tail(1).values[0]) == "2018-04-05T00:00:00.000000000":
            print('debug')
        #tsi est negatif, pas la peine de considerer la vente
        if self.getTrueStrengthWeek(0) < -3:
            return Evaluation(0, self.currentPrice)

        if self.isBullishWeek(0):
            # si en bullish week, on vend seulement si plus growing bullish (ameriorer en utilisant momentum week)
            if self.isGrowingBullishWeek(1) and not self.isGrowingBullishWeek(0):
                return Evaluation(1, self.currentPrice)
            else:
                return Evaluation(0, self.currentPrice)
        else:
            # si on etait en bullish week la semaine d'avant alors on vend
            if self.isBullishWeek(1):
                return Evaluation(1, self.currentPrice)
            # si on est en bearish week et qu'on a de la currency, il faut vendre dès qu'on est plus en bullish day
            if self.isGrowingBullishDay(1) and not self.isGrowingBullishDay(0):
                return Evaluation(1, self.currentPrice)

        return Evaluation(0.5, self.currentPrice)

