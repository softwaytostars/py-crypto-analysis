import os


def getFromToCurrencies(symbol):
    return getFromCurrency(symbol), getToCurrency(symbol)


def getFromCurrency(symbol):
    return symbol[0:3]


def getToCurrency(symbol):
    return symbol[3:]


def sortByProba(symbols, dictEvalBuy):
    symbols.sort(key=lambda symbol: dictEvalBuy[symbol].proba, reverse=True)


def profitForSell(symbol, dictEvalSell, wallet):
    return dictEvalSell[symbol].price - wallet.mean_cost_origin(getFromCurrency(symbol))


def sortByProfit(symbols, dictEvalSell, wallet):
    symbols.sort(key=lambda symbol: profitForSell(symbol, dictEvalSell, wallet),
                 reverse=True)

def load_properties_from_file(relative_path):
    props = {}
    project_dir = os.path.dirname(__file__)
    with open(os.path.join(project_dir, relative_path)) as f:
        for line in f.readlines():
            key, value = line.split("=")
            props[key.strip()] = value.strip()
    return props