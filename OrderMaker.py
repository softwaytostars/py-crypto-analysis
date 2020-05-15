from Model import Side
from Utils import getFromToCurrencies


class Order(object):
    def __init__(self, tuple):
        self.tuple = tuple

    def getSymbol(self):
        return self.tuple[0]

    def getPrice(self):
        return self.tuple[1]

    def getSide(self):
        return self.tuple[2]

    def getAmount(self):
        return self.tuple[3]


class OrderMaker(object):
    def __init__(self, wallet):
        self.wallet = wallet
        self.orders = []

    def __onOrderExecuted__(self, symbol, price, side, amount):
        (fromcurr, tocurr) = getFromToCurrencies(symbol)
        # consider as executed for sell for not consider the amount
        # for buy do not consider as yours for now
        if side == Side.SELL:
            self.wallet.removeFromWallet(fromcurr, amount)
            amountInToCurrency = amount * price
            self.wallet.addToWalletWithOrigin(tocurr, symbol, price, amountInToCurrency)
        else:
            amountInFromCurrency = amount / price
            self.wallet.addToWalletWithOrigin(fromcurr, symbol, price, amountInFromCurrency)
            self.wallet.removeFromWallet(tocurr, amount)

    def makeOrder(self, symbol, price, side, amount):
        if amount < 0:
            return None
        order = (symbol, price, side, amount)
        self.orders.append(order)
        return Order(order)

    def executeOrders(self):
        for order in self.orders:
            self.__onOrderExecuted__(order[0], order[1], order[2], order[3])
        self.orders.clear()

    def printOrders(self):
        if len(self.orders) > 0:
            print('orders to make :')
            for order in self.orders:
                print(repr(order))
