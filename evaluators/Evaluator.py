from abc import ABC


class Evaluator(ABC):
    def __init__(self):
        self.dataWeekEvaluation = None
        self.dataDayEvaluation = None
        self.currentPrice = None

    def initWithData(self, dataWeekEvaluation, dataDayEvaluation, currentPrice):
        self.dataWeekEvaluation = dataWeekEvaluation
        self.dataDayEvaluation = dataDayEvaluation
        self.currentPrice = currentPrice

    def getOpenTimeDay(self, n):
        return self.dataDayEvaluation.tail(n + 1).index.values[0]

    def getOpenTimeWeek(self, n):
        return self.dataWeekEvaluation.tail(n + 1).index.values[0]

    def getStrDateOpenTimeDay(self, n):
        return self.dataDayEvaluation['datetime'].tail(n + 1).values[0]

    def getNWeekFromNDay(self, nDay):
        intervalWeek = self.getOpenTimeWeek(0) - self.getOpenTimeWeek(1)
        openTimeDay = self.getOpenTimeDay(nDay)

        nWeek = 0
        weekfound = False
        while not weekfound:
            openTimeWeek = self.getOpenTimeWeek(nWeek)
            weekfound = openTimeWeek <= openTimeDay < openTimeWeek + intervalWeek
            if weekfound:
                return nWeek
            nWeek += 1
        return None

    def getLowerDataWeekPrice(self, n):
        return self.dataWeekEvaluation['Low'].tail(n + 1).values[0]

    def getHigherDataWeekPrice(self, n):
        return self.dataWeekEvaluation['High'].tail(n + 1).values[0]

    def getLowerDataDayPrice(self, n):
        return self.dataDayEvaluation['Low'].tail(n + 1).values[0]

    def getHigherDataDayPrice(self, n):
        return self.dataDayEvaluation['High'].tail(n + 1).values[0]

    def getCloseDataDayPrice(self, n):
        return self.dataDayEvaluation['Close'].tail(n + 1).values[0]

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

    def getStrengthADXWeek(self, n):
        return self.dataWeekEvaluation['adx'].tail(n + 1).values[0]

    def getStrengthADXDay(self, n):
        return self.dataDayEvaluation['adx'].tail(n + 1).values[0]

    def getStrengthADXPosDay(self, n):
        return self.dataDayEvaluation['pos_directional_indicator'].tail(n + 1).values[0]

    def getStrengthADXNegDay(self, n):
        return self.dataDayEvaluation['neg_directional_indicator'].tail(n + 1).values[0]

    def getTrueStrengthWeek(self, n):
        return self.dataWeekEvaluation['tsi'].tail(n + 1).values[0]

    def getTrueStrengthDay(self, n):
        return self.dataDayEvaluation['tsi'].tail(n + 1).values[0]

    def getTrueStrengthEMAWeek(self, n):
        return self.dataWeekEvaluation['ematsi'].tail(n + 1).values[0]

    def getTrueStrengthEMADay(self, n):
        return self.dataDayEvaluation['ematsi'].tail(n + 1).values[0]

    def getTauxStrengthDay(self, n):
        return self.dataDayEvaluation['tauxtsi'].tail(n + 1).values[0]

    def getEcartTopBottomBollingerDay(self, n):
        return self.getTopBollingerDay(n) - self.getBottomBollingerDay(n)

    def getMidBollingerDay(self, n):
        return self.dataDayEvaluation['bollinger_mid'].tail(n + 1).values[0]

    def getTopBollingerDay(self, n):
        return self.dataDayEvaluation['bollinger_top'].tail(n + 1).values[0]

    def getBottomBollingerDay(self, n):
        return self.dataDayEvaluation['bollinger_bottom'].tail(n + 1).values[0]

    def isTauxStrengthDayEnought(self, n):
        return self.getTauxStrengthDay(n) > 20

    def isBullishWeek(self, n):
        return self.getLowerDataWeekPrice(n) > self.getSARWeek(n) \
               and (self.getMacdHistoWeek(n) >= 0
                    or (self.getMacdHistoWeek(n) > self.getMacdHistoWeek(n + 1) and self.getMacdSignalWeek(n) < 0))

    def isGrowingBullishWeek(self, n):
        return self.getLowerDataWeekPrice(n) > self.getSARWeek(n) \
               and self.getAOWeek(n) > self.getAOWeek(n + 1) \
               and (self.getMacdHistoWeek(n) > 0 or (self.getMacdHistoWeek(n) > self.getMacdHistoWeek(n + 1))) \
               and self.getTrueStrengthWeek(n) > self.getTrueStrengthWeek(n + 1)

    def isStillGrowingBullishWeek(self, n):
        return self.getLowerDataWeekPrice(n) > self.getSARWeek(n) \
               and self.getAOWeek(n) > self.getAOWeek(n + 1) \
               and (self.getMacdHistoWeek(n) > 0 or (self.getMacdHistoWeek(n) > self.getMacdHistoWeek(n + 1))) \
               and self.getTrueStrengthWeek(n) > self.getTrueStrengthEMAWeek(n)

    def increaseOrLightDecrease(self, previous, next, percent):
        return (next >= previous) or 100 * abs(next - previous) / abs(previous) < percent

    # pour pas sortir trop vite
    def isStillGrowingIfBullishSARDay(self, n):
        if self.isBullishDay(n):
            return self.getCoppockDay(n) > self.getCoppockDay(n + 2) \
                   and self.getTrueStrengthDay(n) > self.getTrueStrengthDay(n + 2)
        return True

    def isWorthToBuyInBearishWeek(self, n):
        return 100 * (self.getSARWeek(n) - self.currentPrice) / self.currentPrice > 100

    def isGrowingBullishDay(self, n):
        return self.getAODay(n) > self.getAODay(n + 1) \
               and self.priceCanGrowInDay(n)

    def priceCanGrowInDay(self, n):
        ARBITRARY_THREASHOLD = 2
        diffpercent = 100 * (self.getTrueStrengthDay(n) / self.getTrueStrengthEMADay(n) - 1)
        # return diffpercent > ARBITRARY_THREASHOLD \
        #         or (abs(diffpercent) < 2 and (self.getTrueStrengthDay(n) > self.getTrueStrengthDay(n+1)))
        #        # and ((self.getStrengthADXPosDay(n) >= self.getStrengthADXNegDay(n))
        #        #      or (self.getStrengthADXNegDay(n)-self.getStrengthADXPosDay(n) < self.getStrengthADXNegDay(n+1)-self.getStrengthADXPosDay(n+1)))
        return self.getTrueStrengthDay(n) > self.getTrueStrengthEMADay(n) and diffpercent > 2
        # and  (self.getStrengthADXDay(n) > 30)


    def priceIsGoingToGrowInDay(self, n):
        ARBITRARY_THRESHOLD = 5
        positiveAscension = (self.getStrengthADXPosDay(n) > self.getStrengthADXNegDay(n)) or \
        (self.getStrengthADXPosDay(n) > self.getStrengthADXPosDay(n + 2) and self.getStrengthADXNegDay(n) < self.getStrengthADXNegDay(n + 2))

        ratiodiff = 100*abs((self.getTrueStrengthDay(n) - self.getTrueStrengthEMADay(n))/self.getTrueStrengthEMADay(n))

        return self.getTrueStrengthDay(n) > self.getTrueStrengthDay(n + 1) \
                and self.getTrueStrengthDay(n + 1) > self.getTrueStrengthDay(n + 2) \
                and abs(self.getTrueStrengthDay(n) - self.getTrueStrengthEMADay(n)) < abs(self.getTrueStrengthDay(n + 1) - self.getTrueStrengthEMADay(n + 1)) \
                and positiveAscension \
                and ratiodiff < ARBITRARY_THRESHOLD

    def trueStrengthDayDecrease(self, n):
        return self.getTrueStrengthDay(n) < self.getTrueStrengthDay(n + 1)

    def isBecomingTrueStrengthBullishDayUnderBullishWeek(self, n):
        return self.getTrueStrengthDay(n) >= self.getTrueStrengthDay(n + 1) \
               and self.getStrengthADXPosDay(n) > self.getStrengthADXNegDay(n)\
               and self.isBullishWeek(n)

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

    # def isBullishDayOrFarFromBeginBearishDay(self, n):
    #     if self.isBullishDay(n):
    #         return True
    #     return self.nDaysSinceStopBullishDay(n) > 4