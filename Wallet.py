import copy


class _StockCurrency(object):
    def __init__(self):
        self.fromOrigin = []
        self.mean_cost_origin = 0
        self.totalAmount = 0

    def __calculateMeanCostOrigin__(self):
        self.mean_cost_origin = 0
        weight = 0
        for tupleOrig in self.fromOrigin:
            self.mean_cost_origin += tupleOrig[1] * tupleOrig[2]
            weight += tupleOrig[2]
        self.mean_cost_origin /= weight

    def add_to_wallet_without_origin(self, amount):
        self.totalAmount += amount

    def add_to_wallet_with_origin(self, pairorigin, priceorigin, amount):
        self.fromOrigin.append((pairorigin, priceorigin, amount))
        self.totalAmount += amount
        self.__calculateMeanCostOrigin__()

    def remove_from_wallet(self, amount):
        self.totalAmount -= amount
        if self.totalAmount == 0:
            self.mean_cost_origin = 0

    def copy(self):
        stock = _StockCurrency()
        stock.fromOrigin = self.fromOrigin[:]
        stock.mean_cost_origin = self.mean_cost_origin
        stock.totalAmount = self.totalAmount
        return stock

    def __repr__(self):
        return repr(vars(self))


class Wallet(object):
    def __init__(self):
        self.currentStock = {}

    def add_to_wallet_without_origin(self, currency, amount):
        self.currentStock[currency] = self.currentStock.get(currency, _StockCurrency())
        self.currentStock[currency].add_to_wallet_without_origin(amount)

    def add_to_wallet_with_origin(self, currency, pair_origin, price_origin, amount):
        self.currentStock[currency] = self.currentStock.get(currency, _StockCurrency())
        self.currentStock[currency].add_to_wallet_with_origin(pair_origin, price_origin, amount)

    def remove_from_wallet(self, currency, amount):
        self.currentStock.get(currency).remove_from_wallet(amount)
        if self.currentStock.get(currency).totalAmount == 0:
            del self.currentStock[currency]

    def mean_cost_origin(self, currency):
        return self.currentStock.get(currency, _StockCurrency()).mean_cost_origin

    def amount_for_currency(self, currency):
        return self.currentStock.get(currency, _StockCurrency()).totalAmount

    def copy(self):
        wallet = Wallet()
        for key in self.currentStock:
            wallet.currentStock[key] = self.currentStock[key].copy()
        return wallet

    def __repr__(self):
        return repr(vars(self))
