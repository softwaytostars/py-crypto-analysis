from abc import ABC


class Evaluator(ABC):
    def __init__(self, dataWeekEvaluation, dataDayEvaluation, currentPrice):
        self.dataWeekEvaluation = dataWeekEvaluation
        self.dataDayEvaluation = dataDayEvaluation
        self.currentPrice = currentPrice

    def getLowerDataWeekPrice(self, n):
        return self.dataWeekEvaluation['Low'].tail(n + 1).values[0]

    def getHigherDataWeekPrice(self, n):
        return self.dataWeekEvaluation['High'].tail(n + 1).values[0]

    def getLowerDataDayPrice(self, n):
        return self.dataDayEvaluation['Low'].tail(n + 1).values[0]

    def getHigherDataDayPrice(self, n):
        return self.dataDayEvaluation['High'].tail(n + 1).values[0]

    def getSARWeek(self, n):
        return self.dataWeekEvaluation['SAR'].tail(n + 1).values[0]

    def getSARDay(self, n):
        return self.dataDayEvaluation['SAR'].tail(n + 1).values[0]

    def getAOWeek(self, n):
        return self.dataWeekEvaluation['ao'].tail(n + 1).values[0]

    def getAODay(self, n):
        return self.dataDayEvaluation['ao'].tail(n + 1).values[0]

    def getMacdSignalWeek(self, n):
        return self.dataWeekEvaluation['macd_signal'].tail(n + 1).values[0]

    def getMacdHistoWeek(self, n):
        return self.dataWeekEvaluation['macd_histo'].tail(n + 1).values[0]

    def getMacdHistoDay(self, n):
        return self.dataDayEvaluation['macd_histo'].tail(n + 1).values[0]

    def getCoppockDay(self, n):
        return self.dataDayEvaluation['coppock'].tail(n + 1).values[0]

    def getStrengthADX(self, n):
        return self.dataWeekEvaluation['adx'].tail(n + 1).values[0]

    def getTrueStrengthWeek(self, n):
        return self.dataWeekEvaluation['tsi'].tail(n + 1).values[0]

    def getTrueStrengthDay(self, n):
        return self.dataDayEvaluation['tsi'].tail(n + 1).values[0]

    def getTrueStrengthEMAWeek(self, n):
        return self.dataWeekEvaluation['ematsi'].tail(n + 1).values[0]

    def getTauxStrengthDay(self, n):
        return self.dataDayEvaluation['tauxtsi'].tail(n + 1).values[0]

    def isTauxStrengthDayEnought(self, n):
        return self.getTauxStrengthDay(n) > 20

    def isBullishWeek(self, n):
        return self.getLowerDataWeekPrice(n) > self.getSARWeek(n) \
               and (self.getMacdHistoWeek(n) >= 0
                    or (self.getMacdHistoWeek(n) > self.getMacdHistoWeek(n + 1) and self.getMacdSignalWeek(n) < 0))

    def isGrowingBullishWeek(self, n):
        return self.getLowerDataWeekPrice(n) > self.getSARWeek(n) \
               and self.getAOWeek(n) > self.getAOWeek(n + 1) \
               and (self.getMacdHistoWeek(n) > 0 or (self.getMacdHistoWeek(n) > self.getMacdHistoWeek(n+1))) \
               and self.getTrueStrengthWeek(n) > self.getTrueStrengthWeek(n + 1)

    def increaseOrLightDecrease(self, previous, next, percent):
        return (next >= previous) or 100 * abs(next - previous) / abs(previous) < percent

    # pour pas sortir trop vite
    def isStillGrowingIfBullishSARDay(self, n):
        if self.isBullishDay(n):
           return self.getCoppockDay(n) > self.getCoppockDay(n + 2) \
                  and self.getTrueStrengthDay(n) > self.getTrueStrengthDay(n + 2)
        return True

    def isWorthToBuyInBearishWeek(self, n):
        return 100*(self.getSARWeek(n)-self.currentPrice)/self.currentPrice > 100

    def isGrowingBullishDay(self, n):
        return self.increaseOrLightDecrease(self.getCoppockDay(n + 1), self.getCoppockDay(n), 4) \
               and self.getAODay(n) > self.getAODay(n + 1) \
               and self.increaseOrLightDecrease(self.getTrueStrengthDay(n + 1), self.getTrueStrengthDay(n), 4) \
               and self.isStillGrowingIfBullishSARDay(n)

    def strengthIsIncreasingWeek(self, n):
        # soit le strength augmente, soit il se stabilise après une baisse
        return (self.getTrueStrengthWeek(n) > self.getTrueStrengthWeek(n + 1)) \
               or ((self.getTrueStrengthWeek(n) == self.getTrueStrengthWeek(n + 1))
                   and self.getTrueStrengthWeek(n + 1) < self.getTrueStrengthWeek(n + 2))

    def isBullishDay(self, n):
        return self.getLowerDataDayPrice(n) > self.getSARDay(n)

    def nDaysSinceStopBullishDay(self, n):
        i = 0
        while not self.isBullishDay(n + i):
            i += 1
        return i

    def isBullishDayOrFarFromBeginBearishDay(self, n):
        if self.isBullishDay(n):
            return True
        return self.nDaysSinceStopBullishDay(n) > 4
