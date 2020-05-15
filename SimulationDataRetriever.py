from DataRetriever import DataRetriever


class SimulationDataRetriever(DataRetriever):
    def getCurrentPrice(self, symbol, opentime):
        currentData = self.allDataWeekFrame.loc[(self.allDataWeekFrame.index.get_level_values('opentime') == opentime) &
                                            (self.allDataWeekFrame.index.get_level_values('symbol') == symbol)]
        return float(currentData.Close.values[0])
