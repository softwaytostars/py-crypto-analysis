from evaluators.Evaluation import Evaluation
from evaluators.Evaluator import Evaluator


class EvaluatorHandler(Evaluator):
    def __getInfosMaximumTrueStrenghDay__(self, n):
        if self.getTrueStrengthDay(n) < self.getTrueStrengthDay(n + 1) \
                and self.getTrueStrengthDay(n + 1) > self.getTrueStrengthDay(n + 2) \
                and self.getTrueStrengthDay(n + 1) > self.getTrueStrengthEMADay(n + 1):
            return self.getOpenTimeDay(n + 1), self.getTrueStrengthDay(n + 1), n + 1
        else:
            return None

    def __lookForLastMaximumTrueStrenghDay__(self, fromN, conditionWeek):
        n = fromN
        lastMaximumInfos = None
        while lastMaximumInfos is None and conditionWeek(self.getNWeekFromNDay(n)):
            strdate = self.getStrDateOpenTimeDay(n)
            lastMaximumInfos = self.__getInfosMaximumTrueStrenghDay__(n)
            n = n + 1
        return lastMaximumInfos

    def __calculatePenteTrueStrenghDay__(self, fromN):
        previous = None
        last = self.__lookForLastMaximumTrueStrenghDay__(fromN, self.isBullishWeek)
        if last is not None:
            previous = self.__lookForLastMaximumTrueStrenghDay__(last[2], self.isBullishWeek)
        if last is not None and previous is not None:
            return (last[1] - previous[1]) / (last[0] - previous[0]), previous[2]
        else:
            return None

    def StrengthDayIsWeakeningBetweenMax(self, n):
        lastPente = self.__calculatePenteTrueStrenghDay__(n)
        if lastPente is None:
            return False
        if lastPente[0] <= 0:
            return True
        previousPente = self.__calculatePenteTrueStrenghDay__(lastPente[1])
        if previousPente is None:
            return False
        return lastPente[0] < previousPente[0]

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
        return self.priceCanGrowInDay(1) and not self.priceCanGrowInDay(0)

    def rateDecreaseEcartBollingDay(self):
        return 100*(self.getEcartTopBottomBollingerDay(1)/self.getEcartTopBottomBollingerDay(0) -1)

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

    def evaluateBuy(self):

        if str(self.dataDayEvaluation['datetime'].tail(1).values[0]) == "2019-07-31T00:00:00.000000000":
            print('debug')
            print(self.getStrengthADXPosDay(0))
            print(self.getStrengthADXNegDay(0))

        if self.getStrengthADXDay(0) < 30:
            return Evaluation(0, self.currentPrice)

        if self.isGrowingBullishWeek(0):
            # si on entre toute juste en bullish week growing, faut acheter
            if not self.isGrowingBullishWeek(self.getNWeekFromNDay(1)):
                return Evaluation(1, self.currentPrice)
            # elif self.isGrowingBullishDay(0):
            #     return Evaluation(0.9, self.currentPrice)

        if self.isBullishWeek(0):
            if self.priceIsGoingToGrowInDay(0):
                return Evaluation(1, self.currentPrice)
        else:
            if self.getStrengthADXDay(0) < 30:
                return Evaluation(0, self.currentPrice)
            if self.priceIsGoingToGrowInDay(0) and self.rateDecreaseEcartBollingDay() < 15:
                return Evaluation(0.8, self.currentPrice)


        # if on est en bearish week mais qu'on entre en bullish day, faut acheter
        # mais seulement si l'ecart bollinger est pas en diminution trop forte
        #and self.isGrowingBullishDay(0)

        return Evaluation(0, self.currentPrice)

    def evaluateSell(self):
        if str(self.dataDayEvaluation['datetime'].tail(1).values[0]) == "2020-02-02T00:00:00.000000000":
            print('debug')
        # tsi est negatif, pas la peine de considerer la vente
        if self.getTrueStrengthWeek(0) < -3:
            return Evaluation(0, self.currentPrice)

        if self.isBullishWeek(0):
            # si en bullish week, on vend seulement si plus growing bullish (ameriorer en utilisant momentum week)
            if self.isStillGrowingBullishWeek(1) and not self.isStillGrowingBullishWeek(0):
                return Evaluation(1, self.currentPrice)
            # elif self.priceCannotGrowMoreInDay() and self.StrengthDayIsWeakeningBetweenMax(0):
            elif self.StrengthDayIsWeakeningBetweenMax(0):
                return Evaluation(1, self.currentPrice)
            else:
                return Evaluation(0, self.currentPrice)
        else:
            # si on etait en bullish week la semaine d'avant alors on vend
            if self.isBullishWeek(self.getNWeekFromNDay(1)):
                return Evaluation(1, self.currentPrice)
            # si on est en bearish week et qu'on a de la currency, il faut vendre dès qu'on est plus en bullish day
            ## ou bien qu"on a atteint la resistance
            if self.priceCannotGrowMoreInDay() or (self.trueStrengthDayDecrease(0) and self.isAgainstResistance(0)):
                return Evaluation(1, self.currentPrice)

        return Evaluation(0.5, self.currentPrice)
