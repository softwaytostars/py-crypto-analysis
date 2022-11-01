from evaluators.Evaluation import Evaluation
from evaluators.TradingToolCalculator import TradingToolCalculator


# TODO the handler should be able to handle different strategies instead
class EvaluatorHandler:
    def __init__(self):
        self.tool_trading = TradingToolCalculator()
        self.enter_growing_bullish_week = None
        self.current_price = None

    def __get_infos_maximum_true_strengh_day__(self, n):
        if self.tool_trading.getTSIDay(n) < self.tool_trading.getTSIDay(n + 1) \
                and self.tool_trading.getTSIDay(n + 1) > self.tool_trading.getTSIDay(n + 2) \
                and self.tool_trading.getTSIDay(n + 1) > self.tool_trading.getTSIEMADay(n + 1):
            return self.tool_trading.getOpenTimeDay(n + 1), self.tool_trading.getTSIDay(n + 1), n + 1
        else:
            return None

    def __getInfosMinimumTrueStrenghDay__(self, n):
        if self.tool_trading.getTSIDay(n) > self.tool_trading.getTSIDay(n + 1) \
                and self.tool_trading.getTSIDay(n + 1) < self.tool_trading.getTSIDay(n + 2):
            return self.tool_trading.getOpenTimeDay(n + 1), self.tool_trading.getTSIDay(n + 1), n + 1
        else:
            return None

    def __lookForLastMaximumTrueStrenghDay__(self, fromN, conditionWeek):
        n = fromN
        last_maximum_infos = None
        while last_maximum_infos is None and conditionWeek(self.tool_trading.getNWeekFromNDay(n)):
            last_maximum_infos = self.__get_infos_maximum_true_strengh_day__(n)
            n = n + 1
        return last_maximum_infos

    def __lookForLastMinimumTrueStrenghDay__(self, fromN):
        n = fromN
        last_minimum_infos = None
        while last_minimum_infos is None:
            last_minimum_infos = self.__getInfosMinimumTrueStrenghDay__(n)
            n = n + 1
        return last_minimum_infos

    def is_coming_from_minimum_tsi_below_ema_day(self, n):
        last_mini = self.__lookForLastMinimumTrueStrenghDay__(n)
        if last_mini is None:
            return False
        return last_mini[1] < self.tool_trading.getTSIEMADay(last_mini[2])

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

    def isTauxStrengthDayEnought(self, n):
        return self.tool_trading.getTauxStrengthDay(n) > 20

    def isBullishWeek(self, n):
        return self.tool_trading.getLowerDataWeekPrice(n) > self.tool_trading.getSARWeek(n) \
               and (self.tool_trading.getMacdHistoWeek(n) >= 0
                    or (self.tool_trading.getMacdHistoWeek(n) > self.tool_trading.getMacdHistoWeek(n + 1) and self.tool_trading.getMacdSignalWeek(n) < 0))

    def isBullishSarWeek(self, n):
        return self.tool_trading.getLowerDataWeekPrice(n) > self.tool_trading.getSARWeek(n)

    def isGrowingBullishWeek(self, n):
        return self.tool_trading.getLowerDataWeekPrice(n) > self.tool_trading.getSARWeek(n) \
               and self.tool_trading.getAOWeek(n) > self.tool_trading.getAOWeek(n + 1) \
               and (self.tool_trading.getMacdHistoWeek(n) > 0 or (self.tool_trading.getMacdHistoWeek(n) > self.tool_trading.getMacdHistoWeek(n + 1))) \
               and self.tool_trading.getTSIWeek(n) > self.tool_trading.getTSIWeek(n + 1)

    def isStillGrowingBullishWeek(self, n):
        return self.tool_trading.getLowerDataWeekPrice(n) > self.getSARWeek(n) \
               and self.tool_trading.getAOWeek(n) > self.tool_trading.getAOWeek(n + 1) \
               and (self.tool_trading.getMacdHistoWeek(n) > 0 or (self.tool_trading.getMacdHistoWeek(n) > self.tool_trading.getMacdHistoWeek(n + 1))) \
               and self.tool_trading.getTSIWeek(n) > self.tool_trading.getTSIEMAWeek(n)

    def increaseOrLightDecrease(self, previous, next, percent):
        return (next >= previous) or 100 * abs(next - previous) / abs(previous) < percent

    # pour pas sortir trop vite
    def isStillGrowingIfBullishSARDay(self, n):
        if self.isBullishDay(n):
            return self.tool_trading.getCoppockDay(n) > self.tool_trading.getCoppockDay(n + 2) \
                   and self.tool_trading.getTSIDay(n) > self.tool_trading.getTSIDay(n + 2)
        return True

    def isWorthToBuyInBearishWeek(self, n):
        return 100 * (self.getSARWeek(n) - self.current_price) / self.current_price > 100

    def isGrowingBullishDay(self, n):
        return self.tool_trading.getAODay(n) > self.tool_trading.getAODay(n + 1) \
               and self.priceCanGrowInDay(n)

    def priceCanGrowInDay(self, n):
        ARBITRARY_THREASHOLD = 2
        diffpercent = 100 * (self.getTSIDay(n) / self.getTSIEMADay(n) - 1)
        # return diffpercent > ARBITRARY_THREASHOLD \
        #         or (abs(diffpercent) < 2 and (self.getTSIDay(n) > self.getTSIDay(n+1)))
        #        # and ((self.getDMIADXPosDay(n) >= self.getDMIADXNegDay(n))
        #        #      or (self.getDMIADXNegDay(n)-self.getDMIADXPosDay(n) < self.getDMIADXNegDay(n+1)-self.getDMIADXPosDay(n+1)))
        return self.tool_trading.getTSIDay(n) > self.tool_trading.getTSIEMADay(n) and diffpercent > 2
        # and  (self.getDMIADXDay(n) > 30)

    def directionPriceIsUpAccordingADX(self, n):
        ARBITRARY_THRESHOLD = 5
        ratiodiff = 100 *(self.tool_trading.getDMIADXNegDay(n)/self.tool_trading.getDMIADXPosDay(n) -1)
        positiveAscension = (self.tool_trading.getDMIADXPosDay(n) > self.tool_trading.getDMIADXNegDay(n)) or \
                            ((self.tool_trading.getDMIADXPosDay(n) > self.tool_trading.getDMIADXPosDay(n + 2)) \
                             and (self.tool_trading.getDMIADXNegDay(n) < self.tool_trading.getDMIADXNegDay(n + 2)) \
                             and ratiodiff < ARBITRARY_THRESHOLD)
        return positiveAscension

    def directionPriceIsUpAccordingTSI(self, n):
        ARBITRARY_THRESHOLD = 5
        ratiodiff = 100 *(self.tool_trading.getTSIEMADay(n)/self.tool_trading.getTSIDay(n) - 1)
        positiveAscension = (self.tool_trading.getTSIDay(n) > self.tool_trading.getTSIEMADay(n)) or \
                            ((self.tool_trading.getDMIADXPosDay(n) > self.tool_trading.getDMIADXPosDay(n + 1)) \
                             and ratiodiff < ARBITRARY_THRESHOLD)
        return positiveAscension

    def priceIsGoingToGrowInDay(self, n):
        return self.directionPriceIsUpAccordingADX(n) \
               and self.directionPriceIsUpAccordingTSI(n) \
               and self.tool_trading.getMacdHistoDay(n) > 1

    def trueStrengthDayDecrease(self, n):
        return self.tool_trading.getTSIDay(n) < self.tool_trading.getTSIDay(n + 1)

    def trueStrengthDayIncrease(self, n):
        return self.tool_trading.getTSIDay(n) > self.tool_trading.getTSIDay(n + 1)

    def isBecomingTrueStrengthBullishDayUnderBullishWeek(self, n):
        return self.tool_trading.getTSIDay(n) >= self.tool_trading.getTSIDay(n + 1) \
               and self.tool_trading.getDMIADXPosDay(n) > self.tool_trading.getDMIADXNegDay(n) \
               and self.isBullishWeek(n)

    def strengthIsIncreasingWeek(self, n):
        # soit le strength augmente, soit il se stabilise après une baisse
        return (self.tool_trading.getTSIWeek(n) > self.tool_trading.getTSIWeek(n + 1)) \
               or ((self.tool_trading.getTSIWeek(n) == self.tool_trading.getTSIWeek(n + 1))
                   and self.tool_trading.getTSIWeek(n + 1) < self.tool_trading.getTSIWeek(n + 2))

    def isBullishDay(self, n):
        return self.tool_trading.getLowerDataDayPrice(n) > self.tool_trading.getSARDay(n)

    def nDaysSinceStopBullishDay(self, n):
        i = 0
        while not self.isBullishDay(n + i):
            i += 1
        return i

    def nDaysSinceBullishDay(self, n):
        i = 0
        while self.isBullishDay(n + i):
            i += 1
        return i


    # def isBullishDayOrFarFromBeginBearishDay(self, n):
    #     if self.isBullishDay(n):
    #         return True
    #     return self.nDaysSinceStopBullishDay(n) > 4
    def strength_day_is_weakening_between_max(self, n):
        last_mini = self.__lookForLastMinimumTrueStrenghDay__(n)
        up_to = None
        if last_mini is not None:
            up_to = last_mini[2]
        last_pente = self.__calculatePenteTrueStrenghDay__(n, up_to)
        if last_pente is None:
            return False
        if last_pente[0] <= 0:
            return True
        previous_pente = self.__calculatePenteTrueStrenghDay__(last_pente[1], None)
        if previous_pente is None:
            return False
        return last_pente[0] < previous_pente[0]

    def consider_maximums_tsi(self, n):
        return self.tool_trading.getTSIDay(n) > self.tool_trading.getTSIEMADay(n) \
               and self.tool_trading.getTSIDay(n + 1) > self.tool_trading.getTSIEMADay(n + 1) \
               and self.tool_trading.getTSIDay(n + 2) > self.tool_trading.getTSIEMADay(n + 2)

    def initWithData(self, data_week_evaluation, data_day_evaluation, current_price):
        self.current_price = current_price
        self.tool_trading.initWithData(data_week_evaluation, data_day_evaluation)
        if not self.isGrowingBullishWeek(0):
            self.enter_growing_bullish_week = False
        else:
            if self.enter_growing_bullish_week:
                self.enter_growing_bullish_week = False
            else:
                self.enter_growing_bullish_week = True

    def price_cannot_grow_more_in_day(self):
        return self.priceIsGoingToGrowInDay(1) and not self.priceIsGoingToGrowInDay(0)

    def rate_decrease_ecart_bolling_day(self):
        return 100 * (self.getEcartTopBottomBollingerDay(1) / self.getEcartTopBottomBollingerDay(0) - 1)

    def is_against_resistance(self, n):
        ARBITRARY_THRESHOLD = 2
        if self.tool_trading.getCloseDataDayPrice(n) >= self.tool_trading.getTopBollingerDay(n):
            return True
        diffPercentTop = 100 * (self.tool_trading.getCloseDataDayPrice(n) / self.tool_trading.getTopBollingerDay(n) - 1)
        if abs(diffPercentTop) <= ARBITRARY_THRESHOLD:
            return True
        return False

    def resistanceHasBeenReachedTheseDays(self):
        ARBITRARY_NDAYS = 3
        for i in range(0, ARBITRARY_NDAYS):
            if self.is_against_resistance(i):
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
        if self.tool_trading.getTSIDay(n) > self.tool_trading.getTSIEMADay(n):
            return False
        lastmax = self.__lookForLastMaximumTrueStrenghDay__(n, self.isBullishWeek)
        if lastmax is None:
            return False
        nmax = lastmax[2]
        return self.getDMIADXDay(n) < self.getDMIADXDay(nmax) \
               and self.getMomentumDay(n) < self.getMomentumDay(nmax) \
               and self.tool_trading.getDMIADXPosDay(n) < self.tool_trading.getDMIADXPosDay(nmax) \
               and self.getDMIADXNegDay(n) > self.getDMIADXNegDay(nmax)

    def maxDAndAOEnDeclin(self, n):
        if self.tool_trading.getAODay(n) <= 0:
            return False
        return self.tool_trading.getMacdValueDay(n) < self.tool_trading.getMacdValueDay(n + 1) \
               and self.tool_trading.getAODay(n + 1) > self.tool_trading.getAODay(n + 2) and self.tool_trading.getAODay(n) < self.tool_trading.getAODay(n + 1)

    def aoIsIncreasingSince(self, fromn, ndays):
        for i in range(ndays):
            if self.tool_trading.getAODay(fromn + i) < self.tool_trading.getAODay(fromn + i + 1):
                return False
        return True

    def DMI_is_Growing(self, n):
        return self.tool_trading.getDMIADXPosDay(n) > self.tool_trading.getDMIADXPosDay(n + 1) \
               and self.tool_trading.getDMIADXNegDay(n) < self.tool_trading.getDMIADXNegDay(n + 1)

    def DMI_is_GrowingSince(self, n, ndays):
        for i in range(ndays):
            if not self.DMI_is_Growing(n + i):
                return False
        return True

    def TSI_is_Growing(self, n):
        return self.tool_trading.getTSIDay(n) >= self.tool_trading.getTSIEMADay(n) \
               and self.tool_trading.getTSIDay(n) > self.tool_trading.getTSIDay(n + 1)

    def maxDAndAOEnGrowing(self, n):
        if self.tool_trading.getMacdHistoDay(n) < 0:
            return False
        aodayOK = (self.tool_trading.getAODay(n) > self.tool_trading.getAODay(n + 1)) and \
                  (self.tool_trading.getAODay(n) >= 0 or self.aoIsIncreasingSince(n, 5))
        return aodayOK and self.tool_trading.getMacdValueDay(n) > self.tool_trading.getMacdValueDay(n + 1)

    def evaluateBuy(self):

        # if str(self.tool_trading.data_day_evaluation['datetime'].tail(1).values[0]) == "2018-06-07T00:00:00.000000000":
        #     print('debug')
        #
        # if str(self.tool_trading.data_day_evaluation['datetime'].tail(1).values[0]) == "2019-09-20T00:00:00.000000000":
        #     print('debug')
        #     print(self.tool_trading.getDMIADXPosDay(0))
        #     print(self.tool_trading.getDMIADXNegDay(0))

        # en bear market, ne pas acheter si tendances achat/vente convergent pas
        if not self.isBullishSarWeek(0) and not self.directionPriceIsUpAccordingADX(0):
            return Evaluation(0, self.current_price)

        if self.maxDAndAOEnGrowing(0):
            return Evaluation(1, self.current_price)

        # if self.isGrowingBullishWeek(0):
        #     # si on entre toute juste en bullish week growing, faut acheter
        #     if not self.isGrowingBullishWeek(self.getNWeekFromNDay(1)):
        #         return Evaluation(1, self.current_price)
        #     # elif self.isGrowingBullishDay(0):
        #     #     return Evaluation(0.9, self.current_price)
        #
        # if not self.momentumDayIncreaseForAtLeastNdays(0, 2) \
        #         and self.getDMIADXDay(0) < 40 and self.getDMIADXDay(0) < self.getDMIADXDay(1):
        #     return Evaluation(0, self.current_price)
        #
        # if self.isBullishSarWeek(0):
        #     if self.trueStrengthDayIncrease(0) and self.tool_trading.getTSIDay(0) > self.tool_trading.getTSIEMADay(0):
        #         # achete dès que concurrence dmi price
        #         if self.directionPriceIsUpAccordingADX(0) and self.isComingFromMinimumTSIBelowEMADay(0) \
        #                 and not self.StrengthDayIsWeakeningBetweenMax(0):
        #             return Evaluation(0.9, self.current_price)
        #
        # if self.isBullishWeek(0):
        #     if self.priceIsGoingToGrowInDay(0) and self.isComingFromMinimumTSIBelowEMADay(0) \
        #             and not self.StrengthDayIsWeakeningBetweenMax(0):
        #         return Evaluation(1, self.current_price)
        # else:
        #     if self.getDMIADXDay(0) < 20:
        #         return Evaluation(0, self.current_price)
        #     if self.priceIsGoingToGrowInDay(0) and self.rateDecreaseEcartBollingDay() < 15:
        #         return Evaluation(0.8, self.current_price)

        # if on est en bearish week mais qu'on entre en bullish day, faut acheter
        # mais seulement si l'ecart bollinger est pas en diminution trop forte
        # and self.isGrowingBullishDay(0)

        # //Si TSI

        return Evaluation(0, self.current_price)

    def evaluateSell(self):
        # if str(self.tool_trading.data_day_evaluation['datetime'].tail(1).values[0]) == "2019-01-09T00:00:00.000000000":
        #     print('debug')
        # tsi est negatif, pas la peine de considerer la vente
        # if self.tool_trading.getTSIWeek(0) < -3:
        #     return Evaluation(0, self.current_price)

        if self.price_cannot_grow_more_in_day() or (self.trueStrengthDayDecrease(0) and self.is_against_resistance(0)):
            return Evaluation(1, self.current_price)

        if self.maxDAndAOEnDeclin(0):
            return Evaluation(1, self.current_price)

        # if self.isBullishWeek(0):
        #     # si en bullish week, on vend seulement si plus growing bullish (ameriorer en utilisant momentum week)
        #     if self.isStillGrowingBullishWeek(1) and not self.isStillGrowingBullishWeek(0):
        #         return Evaluation(1, self.current_price)
        #     # elif self.priceCannotGrowMoreInDay() and self.StrengthDayIsWeakeningBetweenMax(0):
        #     elif self.considerMaximumsTSI(0) and self.StrengthDayIsWeakeningBetweenMax(0):
        #         return Evaluation(1, self.current_price)
        #     elif self.bullishWeekIsDying(0):
        #         return Evaluation(1, self.current_price)
        #     else:
        #         return Evaluation(0, self.current_price)
        # else:
        #     # si on etait en bullish week la semaine d'avant alors on vend
        #     if self.isBullishWeek(self.getNWeekFromNDay(1)):
        #         return Evaluation(1, self.current_price)
        #     # si on est en bearish week et qu'on a de la currency, il faut vendre dès qu'on est plus en bullish day
        #     ## ou bien qu"on a atteint la resistance
        #     if self.priceCannotGrowMoreInDay() or (self.trueStrengthDayDecrease(0) and self.isAgainstResistance(0)):
        #         return Evaluation(1, self.current_price)

        probaVente = 0
        # si TSI_Week diminue => + 0.1

        # si TSI DAY diminue => +0.1

        # Si DMI Pos Day <= DMI Neg Day => +0.1

        # si bullish SAR week et TSI day last max <= TSI day previous max dans le bullsih week => +0.5

        return Evaluation(0.5, self.current_price)

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

        if str(self.tool_trading.data_day_evaluation['datetime'].tail(1).values[0]) == "2018-04-09T00:00:00.000000000":
            print('debug')

        if str(self.tool_trading.data_day_evaluation['datetime'].tail(1).values[0]) == "2019-01-14T00:00:00.000000000":
            print('debug')

        if not self.isBullishSarWeek(0):
            dmiSignalIsBuy = self.DMI_is_GrowingSince(0, 2) and self.tool_trading.getDMIADXPosDay(0) >= self.tool_trading.getDMIADXNegDay(0)
            tsiSignalIsBuy = self.TSI_is_Growing(0)
            if dmiSignalIsBuy and tsiSignalIsBuy and not self.is_against_resistance(0) and self.nDaysSinceBullishDay(0) <= 3:
                return Evaluation(1, self.current_price)
        else:
            tsiGoToPositive = self.TSI_is_Growing(0) and (self.tool_trading.getTSIDay(0) >= self.tool_trading.getTSIEMADay(0) or self.isMoreOrNearlyThan(self.tool_trading.getTSIDay(0), self.tool_trading.getTSIEMADay(0)))
            dmiGoToPositive = self.DMI_is_Growing(0) and (self.tool_trading.getDMIADXPosDay(0) >= self.tool_trading.getDMIADXNegDay(0) or self.isMoreOrNearlyThan(self.tool_trading.getDMIADXPosDay(0), self.tool_trading.getDMIADXNegDay(0)))
            if tsiGoToPositive and dmiGoToPositive:
                return Evaluation(1, self.current_price)

        return Evaluation(0, self.current_price)

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
        tsiIsFading = self.tool_trading.getTSIDay(0) < self.tool_trading.getTSIDay(1) and self.isLessOrNearlyThan(self.tool_trading.getTSIDay(0), self.tool_trading.getTSIEMADay(0))
        dmiIsFading = self.tool_trading.getDMIADXPosDay(0) < self.tool_trading.getDMIADXPosDay(1) and self.isLessOrNearlyThan(self.tool_trading.getDMIADXPosDay(0), self.tool_trading.getDMIADXNegDay(0))
        if not self.isBullishSarWeek(0):
            if self.tool_trading.getDMIADXDay(0) < 35:
                if tsiIsFading:
                    return Evaluation(1, self.current_price)
            else:
                if self.tool_trading.getDMIADXPosDay(0) <= self.tool_trading.getDMIADXNegDay(0) and self.tool_trading.getDMIADXPosDay(1) > self.tool_trading.getDMIADXNegDay(1):
                    return Evaluation(1, self.current_price)
        else:
            if tsiIsFading or dmiIsFading:
                return Evaluation(1, self.current_price)
            if self.consider_maximums_tsi(0) and self.strength_day_is_weakening_between_max(0):
                return Evaluation(1, self.current_price)

        return Evaluation(0, self.current_price)