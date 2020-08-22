from evaluators.Evaluation import Evaluation
from evaluators.Evaluator import Evaluator


class EvaluatorHandler(Evaluator):
    def __getInfosMaximumTrueStrenghDay__(self, n):
        if self.getTSIDay(n) < self.getTSIDay(n + 1) \
                and self.getTSIDay(n + 1) > self.getTSIDay(n + 2) \
                and self.getTSIDay(n + 1) > self.getTSIEMADay(n + 1):
            return self.getOpenTimeDay(n + 1), self.getTSIDay(n + 1), n + 1
        else:
            return None

    def __getInfosMinimumTrueStrenghDay__(self, n):
        if self.getTSIDay(n) > self.getTSIDay(n + 1) \
                and self.getTSIDay(n + 1) < self.getTSIDay(n + 2):
            return self.getOpenTimeDay(n + 1), self.getTSIDay(n + 1), n + 1
        else:
            return None

    def __lookForLastMaximumTrueStrenghDay__(self, fromN, conditionWeek):
        n = fromN
        lastMaximumInfos = None
        while lastMaximumInfos is None and conditionWeek(self.getNWeekFromNDay(n)):
            lastMaximumInfos = self.__getInfosMaximumTrueStrenghDay__(n)
            n = n + 1
        return lastMaximumInfos

    def __lookForLastMinimumTrueStrenghDay__(self, fromN):
        n = fromN
        lastMinimumInfos = None
        while lastMinimumInfos is None:
            lastMinimumInfos = self.__getInfosMinimumTrueStrenghDay__(n)
            n = n + 1
        return lastMinimumInfos

    def isComingFromMinimumTSIBelowEMADay(self, n):
        lastmini = self.__lookForLastMinimumTrueStrenghDay__(n)
        if lastmini is None:
            return False
        return lastmini[1] < self.getTSIEMADay(lastmini[2])

    def __calculatePenteTrueStrenghDay__(self, fromN, upToNForFirstMaximum):
        previous = None
        last = self.__lookForLastMaximumTrueStrenghDay__(fromN, self.isBullishWeek)
        if last is not None:
            if upToNForFirstMaximum is not None and last[2] > upToNForFirstMaximum:
                return None
            previous = self.__lookForLastMaximumTrueStrenghDay__(last[2], self.isBullishWeek)
        if last is not None and previous is not None:
            return (last[1] - previous[1]) / (last[0] - previous[0]), previous[2]
        else:
            return None

    def StrengthDayIsWeakeningBetweenMax(self, n):
        lastmini = self.__lookForLastMinimumTrueStrenghDay__(n)
        upto = None
        if lastmini is not None:
            upto = lastmini[2]
        lastPente = self.__calculatePenteTrueStrenghDay__(n, upto)
        if lastPente is None:
            return False
        if lastPente[0] <= 0:
            return True
        previousPente = self.__calculatePenteTrueStrenghDay__(lastPente[1], None)
        if previousPente is None:
            return False
        return lastPente[0] < previousPente[0]

    def considerMaximumsTSI(self, n):
        return self.getTSIDay(n) > self.getTSIEMADay(n) \
               and self.getTSIDay(n + 1) > self.getTSIEMADay(n + 1) \
               and self.getTSIDay(n + 2) > self.getTSIEMADay(n + 2)

    def initWithData(self, dataWeekEvaluation, dataDayEvaluation, currentPrice):
        super().initWithData(dataWeekEvaluation, dataDayEvaluation, currentPrice)
        if not self.isGrowingBullishWeek(0):
            self.enterGrowingBullishWeek = False
        else:
            if self.enterGrowingBullishWeek:
                self.enterGrowingBullishWeek = False
            else:
                self.enterGrowingBullishWeek = True

    def priceCannotGrowMoreInDay(self):
        return self.priceIsGoingToGrowInDay(1) and not self.priceIsGoingToGrowInDay(0)

    def rateDecreaseEcartBollingDay(self):
        return 100 * (self.getEcartTopBottomBollingerDay(1) / self.getEcartTopBottomBollingerDay(0) - 1)

    def isAgainstResistance(self, n):
        ARBITRARY_THRESHOLD = 2
        if self.getCloseDataDayPrice(n) >= self.getTopBollingerDay(n):
            return True
        diffPercentTop = 100 * (self.getCloseDataDayPrice(n) / self.getTopBollingerDay(n) - 1)
        if abs(diffPercentTop) <= ARBITRARY_THRESHOLD:
            return True
        return False

    def resistanceHasBeenReachedTheseDays(self):
        ARBITRARY_NDAYS = 3
        for i in range(0, ARBITRARY_NDAYS):
            if self.isAgainstResistance(i):
                return True
        return False

    def momentumDayIncreaseForAtLeastNdays(self, n, ndays):
        for i in range(ndays):
            if self.getMomentumDay(n + i) < self.getMomentumDay(n + 1 + i):
                return False
        return True

    def bullishWeekIsDying(self, n):
        if self.getDMIADXDay(n) > self.getDMIADXDay(n + 1):
            return False
        if self.getTSIDay(n) > self.getTSIEMADay(n):
            return False
        lastmax = self.__lookForLastMaximumTrueStrenghDay__(n, self.isBullishWeek)
        if lastmax is None:
            return False
        nmax = lastmax[2]
        return self.getDMIADXDay(n) < self.getDMIADXDay(nmax) \
               and self.getMomentumDay(n) < self.getMomentumDay(nmax) \
               and self.getDMIADXPosDay(n) < self.getDMIADXPosDay(nmax) \
               and self.getDMIADXNegDay(n) > self.getDMIADXNegDay(nmax)

    def maxDAndAOEnDeclin(self, n):
        if self.getAODay(n) <= 0:
            return False
        return self.getMacdValueDay(n) < self.getMacdValueDay(n + 1) \
               and self.getAODay(n + 1) > self.getAODay(n + 2) and self.getAODay(n) < self.getAODay(n + 1)

    def aoIsIncreasingSince(self, fromn, ndays):
        for i in range(ndays):
            if self.getAODay(fromn + i) < self.getAODay(fromn + i + 1):
                return False
        return True

    def DMI_is_Growing(self, n):
        return self.getDMIADXPosDay(n) > self.getDMIADXPosDay(n + 1) \
               and self.getDMIADXNegDay(n) < self.getDMIADXNegDay(n + 1)

    def DMI_is_GrowingSince(self, n, ndays):
        for i in range(ndays):
            if not self.DMI_is_Growing(n + i):
                return False
        return True

    def TSI_is_Growing(self, n):
        return self.getTSIDay(n) >= self.getTSIEMADay(n) \
               and self.getTSIDay(n) > self.getTSIDay(n + 1)

    def maxDAndAOEnGrowing(self, n):
        if self.getMacdHistoDay(n) < 0:
            return False
        aodayOK = (self.getAODay(n) > self.getAODay(n + 1)) and \
                  (self.getAODay(n) >= 0 or self.aoIsIncreasingSince(n, 5))
        return aodayOK and self.getMacdValueDay(n) > self.getMacdValueDay(n + 1)

    def evaluateBuy(self):

        if str(self.dataDayEvaluation['datetime'].tail(1).values[0]) == "2018-06-07T00:00:00.000000000":
            print('debug')

        if str(self.dataDayEvaluation['datetime'].tail(1).values[0]) == "2019-09-20T00:00:00.000000000":
            print('debug')
            print(self.getDMIADXPosDay(0))
            print(self.getDMIADXNegDay(0))

        # en bear market, ne pas acheter si tendances achat/vente convergent pas
        if not self.isBullishSarWeek(0) and not self.directionPriceIsUpAccordingADX(0):
            return Evaluation(0, self.currentPrice)

        if self.maxDAndAOEnGrowing(0):
            return Evaluation(1, self.currentPrice)

        # if self.isGrowingBullishWeek(0):
        #     # si on entre toute juste en bullish week growing, faut acheter
        #     if not self.isGrowingBullishWeek(self.getNWeekFromNDay(1)):
        #         return Evaluation(1, self.currentPrice)
        #     # elif self.isGrowingBullishDay(0):
        #     #     return Evaluation(0.9, self.currentPrice)
        #
        # if not self.momentumDayIncreaseForAtLeastNdays(0, 2) \
        #         and self.getDMIADXDay(0) < 40 and self.getDMIADXDay(0) < self.getDMIADXDay(1):
        #     return Evaluation(0, self.currentPrice)
        #
        # if self.isBullishSarWeek(0):
        #     if self.trueStrengthDayIncrease(0) and self.getTSIDay(0) > self.getTSIEMADay(0):
        #         # achete dès que concurrence dmi price
        #         if self.directionPriceIsUpAccordingADX(0) and self.isComingFromMinimumTSIBelowEMADay(0) \
        #                 and not self.StrengthDayIsWeakeningBetweenMax(0):
        #             return Evaluation(0.9, self.currentPrice)
        #
        # if self.isBullishWeek(0):
        #     if self.priceIsGoingToGrowInDay(0) and self.isComingFromMinimumTSIBelowEMADay(0) \
        #             and not self.StrengthDayIsWeakeningBetweenMax(0):
        #         return Evaluation(1, self.currentPrice)
        # else:
        #     if self.getDMIADXDay(0) < 20:
        #         return Evaluation(0, self.currentPrice)
        #     if self.priceIsGoingToGrowInDay(0) and self.rateDecreaseEcartBollingDay() < 15:
        #         return Evaluation(0.8, self.currentPrice)

        # if on est en bearish week mais qu'on entre en bullish day, faut acheter
        # mais seulement si l'ecart bollinger est pas en diminution trop forte
        # and self.isGrowingBullishDay(0)

        # //Si TSI

        return Evaluation(0, self.currentPrice)

    def evaluateSell(self):
        if str(self.dataDayEvaluation['datetime'].tail(1).values[0]) == "2019-01-09T00:00:00.000000000":
            print('debug')
        # tsi est negatif, pas la peine de considerer la vente
        # if self.getTSIWeek(0) < -3:
        #     return Evaluation(0, self.currentPrice)

        if self.priceCannotGrowMoreInDay() or (self.trueStrengthDayDecrease(0) and self.isAgainstResistance(0)):
            return Evaluation(1, self.currentPrice)

        if self.maxDAndAOEnDeclin(0):
            return Evaluation(1, self.currentPrice)

        # if self.isBullishWeek(0):
        #     # si en bullish week, on vend seulement si plus growing bullish (ameriorer en utilisant momentum week)
        #     if self.isStillGrowingBullishWeek(1) and not self.isStillGrowingBullishWeek(0):
        #         return Evaluation(1, self.currentPrice)
        #     # elif self.priceCannotGrowMoreInDay() and self.StrengthDayIsWeakeningBetweenMax(0):
        #     elif self.considerMaximumsTSI(0) and self.StrengthDayIsWeakeningBetweenMax(0):
        #         return Evaluation(1, self.currentPrice)
        #     elif self.bullishWeekIsDying(0):
        #         return Evaluation(1, self.currentPrice)
        #     else:
        #         return Evaluation(0, self.currentPrice)
        # else:
        #     # si on etait en bullish week la semaine d'avant alors on vend
        #     if self.isBullishWeek(self.getNWeekFromNDay(1)):
        #         return Evaluation(1, self.currentPrice)
        #     # si on est en bearish week et qu'on a de la currency, il faut vendre dès qu'on est plus en bullish day
        #     ## ou bien qu"on a atteint la resistance
        #     if self.priceCannotGrowMoreInDay() or (self.trueStrengthDayDecrease(0) and self.isAgainstResistance(0)):
        #         return Evaluation(1, self.currentPrice)

        probaVente = 0
        # si TSI_Week diminue => + 0.1

        # si TSI DAY diminue => +0.1

        # Si DMI Pos Day <= DMI Neg Day => +0.1

        # si bullish SAR week et TSI day last max <= TSI day previous max dans le bullsih week => +0.5

        return Evaluation(0.5, self.currentPrice)

    def evaluationProbaBuy(self):
        # Si TSI DAY passe de nenatif à >=0 (ou tres proche) => +0.1
        # Si DMI POs DAY >= DMI Neg Day => +0.1
        # Si bearish SAR week et que SAr day:
        # acheter que si DMOI Pos day >= DMI Neg day et en agumentation depuis >= 2 jours ET TSI DAY >= EMA TSAY DAY ET ADX >= 25
        # ou que ADX eleve et TSI DAY > EMA TSI DAy
        # vendre des que TSI day <= EMA Day OU QUE (TSI POs day <= TSI neg day si adx elevé)
        # Si bullish SAR week:
        # Acheter chaque fois que TSI Day >= EMA TSI (de en dessous à au dessus) OU que DMI POs DAY >= DMI Neg Day en augmentant
        # vendre chaque fois que (TSI day <= EMA TSI day en diminuant et adx day peu eleve ou alors si eleve il diminue) ou que DMI PosDay <= DMI neg Day en diminuant
        #    ou que macimum sommet TSI day au dessus du EMA TSDI say est inferieur au previous

        if str(self.dataDayEvaluation['datetime'].tail(1).values[0]) == "2018-04-09T00:00:00.000000000":
            print('debug')

        if str(self.dataDayEvaluation['datetime'].tail(1).values[0]) == "2019-01-14T00:00:00.000000000":
            print('debug')

        if not self.isBullishSarWeek(0):
            dmiSignalIsBuy = self.DMI_is_GrowingSince(0, 2) and self.getDMIADXPosDay(0) >= self.getDMIADXNegDay(0)
            tsiSignalIsBuy = self.TSI_is_Growing(0)
            if dmiSignalIsBuy and tsiSignalIsBuy and not self.isAgainstResistance(0) and self.nDaysSinceBullishDay(0) <= 3:
                return Evaluation(1, self.currentPrice)
        else:
            tsiGoToPositive = self.TSI_is_Growing(0) and (self.getTSIDay(0) >= self.getTSIEMADay(0) or self.isMoreOrNearlyThan(self.getTSIDay(0), self.getTSIEMADay(0)))
            dmiGoToPositive = self.DMI_is_Growing(0) and (self.getDMIADXPosDay(0) >= self.getDMIADXNegDay(0) or self.isMoreOrNearlyThan(self.getDMIADXPosDay(0), self.getDMIADXNegDay(0)))
            if tsiGoToPositive and dmiGoToPositive:
                return Evaluation(1, self.currentPrice)

        return Evaluation(0, self.currentPrice)

    def distancevaluesAreLessThan(self, valsup, valinf):
        ARBITRARY_THRESHOLD = 5
        percent = 100*(abs(valsup/valinf) - 1)
        return  percent >= 0 and percent < ARBITRARY_THRESHOLD

    def isLessOrNearlyThan(self, val1, val2):
        if val1 < val2:
            return True
        return self.distancevaluesAreLessThan(val1, val2)

    def isMoreOrNearlyThan(self, val1, val2):
        if val1 > val2:
            return True
        return self.distancevaluesAreLessThan(val2, val1)


    def evaluationProbaSell(self):
        if str(self.dataDayEvaluation['datetime'].tail(1).values[0]) == "2019-01-10T00:00:00.000000000":
            print('debug')

        if str(self.dataDayEvaluation['datetime'].tail(1).values[0]) == "2019-02-09T00:00:00.000000000":
            print('debug')

        tsiIsFading = self.getTSIDay(0) < self.getTSIDay(1) and self.isLessOrNearlyThan(self.getTSIDay(0), self.getTSIEMADay(0))
        dmiIsFading = self.getDMIADXPosDay(0) < self.getDMIADXPosDay(1) and self.isLessOrNearlyThan(self.getDMIADXPosDay(0), self.getDMIADXNegDay(0))
        if not self.isBullishSarWeek(0):
            if self.getDMIADXDay(0) < 35:
                if tsiIsFading:
                    return Evaluation(1, self.currentPrice)
            else:
                if self.getDMIADXPosDay(0) <= self.getDMIADXNegDay(0) and self.getDMIADXPosDay(1) > self.getDMIADXNegDay(1):
                    return Evaluation(1, self.currentPrice)
        else:
            if tsiIsFading or dmiIsFading:
                return Evaluation(1, self.currentPrice)
            if self.considerMaximumsTSI(0) and self.StrengthDayIsWeakeningBetweenMax(0):
                return Evaluation(1, self.currentPrice)

        return Evaluation(0, self.currentPrice)