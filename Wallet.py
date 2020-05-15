import copy


class _StockCurrency(object):
    def __init__(self):
        self.fromOrigin = []
        self.meancostOrigin = 0
        self.totalAmount = 0

    def __calculateMeanCostOrigin__(self):
        self.meancostOrigin = 0
        weight = 0
        for tupleorig in self.fromOrigin:
            self.meancostOrigin += tupleorig[1] * tupleorig[2]
            weight += tupleorig[2]
        self.meancostOrigin /= weight

    def addToWalletWithoutOrigin(self, amount):
        self.totalAmount += amount

    def addToWalletWithOrigin(self, pairorigin, priceorigin, amount):
        self.fromOrigin.append((pairorigin, priceorigin, amount))
        self.totalAmount += amount
        self.__calculateMeanCostOrigin__()

    def removeFromWallet(self, amount):
        self.totalAmount -= amount
        if self.totalAmount == 0:
            self.meancostOrigin = 0

    def copy(self):
        stock = _StockCurrency()
        stock.fromOrigin = self.fromOrigin[:]
        stock.meancostOrigin = self.meancostOrigin
        stock.totalAmount = self.totalAmount
        return stock

    def __repr__(self):
        return repr(vars(self))


class Wallet(object):
    def __init__(self):
        self.currentStock = {}

    def addToWalletWithoutOrigin(self, currency, amount):
        self.currentStock[currency] = self.currentStock.get(currency, _StockCurrency())
        self.currentStock[currency].addToWalletWithoutOrigin(amount)

    def addToWalletWithOrigin(self, currency, pairorigin, priceorigin, amount):
        self.currentStock[currency] = self.currentStock.get(currency, _StockCurrency())
        self.currentStock[currency].addToWalletWithOrigin(pairorigin, priceorigin, amount)

    def removeFromWallet(self, currency, amount):
        self.currentStock.get(currency).removeFromWallet(amount)
        if self.currentStock.get(currency).totalAmount == 0:
            del self.currentStock[currency]

    def meanCostOrigin(self, currency):
        return self.currentStock.get(currency, _StockCurrency()).meancostOrigin

    def amountForCurrency(self, currency):
        return self.currentStock.get(currency, _StockCurrency()).totalAmount

    def copy(self):
        wallet = Wallet()
        for key in self.currentStock:
            wallet.currentStock[key] = self.currentStock[key].copy()
        return wallet


    def __repr__(self):
        return repr(vars(self))

