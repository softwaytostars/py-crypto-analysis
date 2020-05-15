import enum

from Utils import getFromToCurrencies

class Order(object):
    def __init__(self, symbol, position, price, amount):
        self.symbol = symbol
        self.position = position
        self.price = price
        self.amount = amount


class DecisionMaker(object):
    def __init__(self, wallet):
        self.positions = {}
        self.wallet = wallet

    def makeDecision(self, symbol, avgprice, previousmacdh, currentmacdh):
        # when macD changes sign from negative to positive => BUY no matter of the price
        if previousmacdh <= 0 and currentmacdh > 0:
            # amount = determineAmountToBuy(symbol, avgprice)
            self.positions[symbol] = Order(symbol, Side.BUY, avgprice, -1)  # amount to be determined
        else:
            currentHold = self.wallet.currentStock.get(symbol, None)
            if currentHold is not None and currentHold.amount > 0:
                # vend si tendance baisse mais aussi si une autre pair est plus interessante et si baisse ici est
                # ridicule comparee au potentiel de hausse
                if previousmacdh > 0 and currentmacdh < previousmacdh and avgprice > currentHold.buyPrice:
                    self.positions[symbol] = Order(symbol, Side.SELL, avgprice, currentHold.amount)

    def determineAmountToBuy(self, symbol, avgprice):
        (fromCurrency, toCurrency) = getFromToCurrencies(symbol)
        # If we don't have any cash in the toCurrency, we cannot buy the from
        availableStockInFromCurrency = self.wallet.currentStock.get(toCurrency, None)
        if availableStockInFromCurrency is None:
            return 0
        # pour le moment, achete avec tout le cash dispo
        return availableStockInFromCurrency.amount

    # pour le moment, ne prend pas en compte les autres pairs, priorites et autres, juste valide decisions
    def takePositions(self):
        for symbol, order in self.positions.items():
            self.wallet


    def evaluate(self, rowdata):


