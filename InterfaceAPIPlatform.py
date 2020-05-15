class SimuOrder(object):
    def __init__(self, timestamp, symbol, side, price, type, quantity):
        self.timestamp = timestamp
        self.symbol = symbol
        self.side = side
        self.price = price
        self.type = type
        self.quantity = quantity


class InterfaceAPIPlatform(object):

    def __init__(self):
        self.pendingOrders = []

    def makeOrder(self, symbol, side, price, type, quantity):
        self.pendingOrders.add(SimuOrder(symbol, side, price, type, quantity))

    def checkOrdersExecuted(self, df):
        if len(self.pendingOrders) > 0:
            olderindex = self.pendingOrders[0].timestamp
            for index, row in df[df.index > olderindex].iterrows():
                for order in self.pendingOrders:
                        