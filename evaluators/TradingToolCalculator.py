class TradingToolCalculator:
    def __init__(self):
        self.data_week_evaluation = None
        self.data_day_evaluation = None

    def initWithData(self, data_week_evaluation, data_day_evaluation):
        self.data_week_evaluation = data_week_evaluation
        self.data_day_evaluation = data_day_evaluation

    def getOpenTimeDay(self, n):
        return self.data_day_evaluation.tail(n + 1).index.values[0]

    def getOpenTimeWeek(self, n):
        return self.data_week_evaluation.tail(n + 1).index.values[0]

    def getStrDateOpenTimeDay(self, n):
        return self.data_day_evaluation['datetime'].tail(n + 1).values[0]

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
        return self.data_week_evaluation['Low'].tail(n + 1).values[0]

    def getHigherDataWeekPrice(self, n):
        return self.data_week_evaluation['High'].tail(n + 1).values[0]

    def getLowerDataDayPrice(self, n):
        return self.data_day_evaluation['Low'].tail(n + 1).values[0]

    def getHigherDataDayPrice(self, n):
        return self.data_day_evaluation['High'].tail(n + 1).values[0]

    def getCloseDataDayPrice(self, n):
        return self.data_day_evaluation['Close'].tail(n + 1).values[0]

    def getSARWeek(self, n):
        return self.data_week_evaluation['SAR'].tail(n + 1).values[0]

    def getSARDay(self, n):
        return self.data_day_evaluation['SAR'].tail(n + 1).values[0]

    def getAOWeek(self, n):
        return self.data_week_evaluation['ao'].tail(n + 1).values[0]

    def getAODay(self, n):
        return self.data_day_evaluation['ao'].tail(n + 1).values[0]

    def getMacdSignalWeek(self, n):
        return self.data_week_evaluation['macd_signal'].tail(n + 1).values[0]

    def getMacdHistoWeek(self, n):
        return self.data_week_evaluation['macd_histo'].tail(n + 1).values[0]

    def getMacdHistoDay(self, n):
        return self.data_day_evaluation['macd_histo'].tail(n + 1).values[0]

    def getMacdValueDay(self, n):
        return self.data_day_evaluation['macd_value'].tail(n + 1).values[0]

    def getCoppockDay(self, n):
        return self.data_day_evaluation['coppock'].tail(n + 1).values[0]

    def getDMIADXWeek(self, n):
        return self.data_week_evaluation['adx'].tail(n + 1).values[0]

    def getDMIADXDay(self, n):
        return self.data_day_evaluation['adx'].tail(n + 1).values[0]

    def getDMIADXPosDay(self, n):
        return self.data_day_evaluation['pos_directional_indicator'].tail(n + 1).values[0]

    def getDMIADXNegDay(self, n):
        return self.data_day_evaluation['neg_directional_indicator'].tail(n + 1).values[0]

    def getTSIWeek(self, n):
        return self.data_week_evaluation['tsi'].tail(n + 1).values[0]

    def getTSIDay(self, n):
        return self.data_day_evaluation['tsi'].tail(n + 1).values[0]

    def getTSIEMAWeek(self, n):
        return self.data_week_evaluation['ematsi'].tail(n + 1).values[0]

    def getTSIEMADay(self, n):
        return self.data_day_evaluation['ematsi'].tail(n + 1).values[0]

    def getTauxStrengthDay(self, n):
        return self.data_day_evaluation['tauxtsi'].tail(n + 1).values[0]

    def getEcartTopBottomBollingerDay(self, n):
        return self.getTopBollingerDay(n) - self.getBottomBollingerDay(n)

    def getMidBollingerDay(self, n):
        return self.data_day_evaluation['bollinger_mid'].tail(n + 1).values[0]

    def getTopBollingerDay(self, n):
        return self.data_day_evaluation['bollinger_top'].tail(n + 1).values[0]

    def getBottomBollingerDay(self, n):
        return self.data_day_evaluation['bollinger_bottom'].tail(n + 1).values[0]

    def getMomentumDay(self, n):
        return self.data_day_evaluation['momentum'].tail(n + 1).values[0]
