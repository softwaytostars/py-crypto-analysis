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

    def getMacdValueDay(self, n):
        return self.dataDayEvaluation['macd_value'].tail(n + 1).values[0]

    def getCoppockDay(self, n):
        return self.dataDayEvaluation['coppock'].tail(n + 1).values[0]

    def getDMIADXWeek(self, n):
        return self.dataWeekEvaluation['adx'].tail(n + 1).values[0]

    def getDMIADXDay(self, n):
        return self.dataDayEvaluation['adx'].tail(n + 1).values[0]

    def getDMIADXPosDay(self, n):
        return self.dataDayEvaluation['pos_directional_indicator'].tail(n + 1).values[0]

    def getDMIADXNegDay(self, n):
        return self.dataDayEvaluation['neg_directional_indicator'].tail(n + 1).values[0]

    def getTSIWeek(self, n):
        return self.dataWeekEvaluation['tsi'].tail(n + 1).values[0]

    def getTSIDay(self, n):
        return self.dataDayEvaluation['tsi'].tail(n + 1).values[0]

    def getTSIEMAWeek(self, n):
        return self.dataWeekEvaluation['ematsi'].tail(n + 1).values[0]

    def getTSIEMADay(self, n):
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

    def getMomentumDay(self, n):
        return self.dataDayEvaluation['momentum'].tail(n + 1).values[0]

    def isTauxStrengthDayEnought(self, n):
        return self.getTauxStrengthDay(n) > 20

    def isBullishWeek(self, n):
        return self.getLowerDataWeekPrice(n) > self.getSARWeek(n) \
               and (self.getMacdHistoWeek(n) >= 0
                    or (self.getMacdHistoWeek(n) > self.getMacdHistoWeek(n + 1) and self.getMacdSignalWeek(n) < 0))

    def isBullishSarWeek(self, n):
        return self.getLowerDataWeekPrice(n) > self.getSARWeek(n)

    def isGrowingBullishWeek(self, n):
        return self.getLowerDataWeekPrice(n) > self.getSARWeek(n) \
               and self.getAOWeek(n) > self.getAOWeek(n + 1) \
               and (self.getMacdHistoWeek(n) > 0 or (self.getMacdHistoWeek(n) > self.getMacdHistoWeek(n + 1))) \
               and self.getTSIWeek(n) > self.getTSIWeek(n + 1)

    def isStillGrowingBullishWeek(self, n):
        return self.getLowerDataWeekPrice(n) > self.getSARWeek(n) \
               and self.getAOWeek(n) > self.getAOWeek(n + 1) \
               and (self.getMacdHistoWeek(n) > 0 or (self.getMacdHistoWeek(n) > self.getMacdHistoWeek(n + 1))) \
               and self.getTSIWeek(n) > self.getTSIEMAWeek(n)

    def increaseOrLightDecrease(self, previous, next, percent):
        return (next >= previous) or 100 * abs(next - previous) / abs(previous) < percent

    # pour pas sortir trop vite
    def isStillGrowingIfBullishSARDay(self, n):
        if self.isBullishDay(n):
            return self.getCoppockDay(n) > self.getCoppockDay(n + 2) \
                   and self.getTSIDay(n) > self.getTSIDay(n + 2)
        return True

    def isWorthToBuyInBearishWeek(self, n):
        return 100 * (self.getSARWeek(n) - self.currentPrice) / self.currentPrice > 100

    def isGrowingBullishDay(self, n):
        return self.getAODay(n) > self.getAODay(n + 1) \
               and self.priceCanGrowInDay(n)

    def priceCanGrowInDay(self, n):
        ARBITRARY_THREASHOLD = 2
        diffpercent = 100 * (self.getTSIDay(n) / self.getTSIEMADay(n) - 1)
        # return diffpercent > ARBITRARY_THREASHOLD \
        #         or (abs(diffpercent) < 2 and (self.getTSIDay(n) > self.getTSIDay(n+1)))
        #        # and ((self.getDMIADXPosDay(n) >= self.getDMIADXNegDay(n))
        #        #      or (self.getDMIADXNegDay(n)-self.getDMIADXPosDay(n) < self.getDMIADXNegDay(n+1)-self.getDMIADXPosDay(n+1)))
        return self.getTSIDay(n) > self.getTSIEMADay(n) and diffpercent > 2
        # and  (self.getDMIADXDay(n) > 30)

    def directionPriceIsUpAccordingADX(self, n):
        ARBITRARY_THRESHOLD = 5
        ratiodiff = 100 *(self.getDMIADXNegDay(n)/self.getDMIADXPosDay(n) -1)
        positiveAscension = (self.getDMIADXPosDay(n) > self.getDMIADXNegDay(n)) or \
                            ((self.getDMIADXPosDay(n) > self.getDMIADXPosDay(n + 2)) \
                             and (self.getDMIADXNegDay(n) < self.getDMIADXNegDay(n + 2)) \
                             and ratiodiff < ARBITRARY_THRESHOLD)
        return positiveAscension

    def directionPriceIsUpAccordingTSI(self, n):
        ARBITRARY_THRESHOLD = 5
        ratiodiff = 100 *(self.getTSIEMADay(n)/self.getTSIDay(n) - 1)
        positiveAscension = (self.getTSIDay(n) > self.getTSIEMADay(n)) or \
                            ((self.getDMIADXPosDay(n) > self.getDMIADXPosDay(n + 1)) \
                             and ratiodiff < ARBITRARY_THRESHOLD)
        return positiveAscension

    def priceIsGoingToGrowInDay(self, n):
        return self.directionPriceIsUpAccordingADX(n) \
               and self.directionPriceIsUpAccordingTSI(n) \
               and self.getMacdHistoDay(n) > 1

    def trueStrengthDayDecrease(self, n):
        return self.getTSIDay(n) < self.getTSIDay(n + 1)

    def trueStrengthDayIncrease(self, n):
        return self.getTSIDay(n) > self.getTSIDay(n + 1)

    def isBecomingTrueStrengthBullishDayUnderBullishWeek(self, n):
        return self.getTSIDay(n) >= self.getTSIDay(n + 1) \
               and self.getDMIADXPosDay(n) > self.getDMIADXNegDay(n) \
               and self.isBullishWeek(n)

    def strengthIsIncreasingWeek(self, n):
        # soit le strength augmente, soit il se stabilise après une baisse
        return (self.getTSIWeek(n) > self.getTSIWeek(n + 1)) \
               or ((self.getTSIWeek(n) == self.getTSIWeek(n + 1))
                   and self.getTSIWeek(n + 1) < self.getTSIWeek(n + 2))

    def isBullishDay(self, n):
        return self.getLowerDataDayPrice(n) > self.getSARDay(n)

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
