def getFromToCurrencies(symbol):
    return getFromCurrency(symbol), getToCurrency(symbol)


def getFromCurrency(symbol):
    return symbol[0:3]


def getToCurrency(symbol):
    return symbol[3:]


def sortByProba(symbols, dictEvalBuy):
    symbols.sort(key=lambda symbol: dictEvalBuy[symbol].proba, reverse=True)


def profitForSell(symbol, dictEvalSell, wallet):
    return dictEvalSell[symbol].price - wallet.meanCostOrigin(getFromCurrency(symbol))


def sortByProfit(symbols, dictEvalSell, wallet):
    symbols.sort(key=lambda symbol: profitForSell(symbol, dictEvalSell, wallet),
                 reverse=True)
