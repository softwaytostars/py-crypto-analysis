from Model import Side
from algo.OrderMaker import OrderMaker
from Utils import getFromToCurrencies, sortByProfit, getFromCurrency, sortByProba, getToCurrency, profitForSell, \
    load_properties_from_file
from evaluators.EvaluatorHandler import EvaluatorHandler


class AlgoTrading(object):
    def __init__(self, allSymbols, wallet):
        self.allSymbols = allSymbols
        self.wallet = wallet
        self.allDataDayFrame = None
        self.allDataWeekFrame = None
        taxes = load_properties_from_file('binance_config.txt')
        self.order_maker = OrderMaker(wallet, taxes)
        self.periodsToUseForEvaluation = 30
        self.interval_week = 0
        # todo pass strategy option
        self.evaluatorHandler = EvaluatorHandler()

    def compute(self, data_week_evaluation, data_day_evaluation, current_price, str_current_date):
        self.evaluatorHandler.initWithData(data_week_evaluation, data_day_evaluation, current_price)

        sell_orders = []
        buy_orders = []

        dict_eval_buy = {}
        dict_eval_sell = {}
        buyable_now = []
        cannot_buy = []
        will_be_sold = []

        # determine evaluation buy/sell for each symbol
        for symbol in self.allSymbols:
            dict_eval_buy[symbol] = self.evaluatorHandler.evaluateBuy() #. evaluationProbaBuy()
            dict_eval_sell[symbol] = self.evaluatorHandler.evaluateSell() # .evaluationProbaSell()
            # what can we buy ?
            (from_curr, to_curr) = getFromToCurrencies(symbol)
            # should sell if probability is greater than 60% (# to be optimized)
            should_be_sold = dict_eval_sell.get(symbol).proba > 0.60
            # should buy if probability is greater than (# to be optimized)
            should_be_bought = dict_eval_buy.get(symbol).proba > 0.70

            if should_be_sold and self.wallet.amount_for_currency(from_curr) > 0:
                will_be_sold.append(symbol)
            if should_be_bought:
                if self.wallet.amount_for_currency(to_curr) > 0:
                    buyable_now.append(symbol)
                else:
                    cannot_buy.append(symbol)

        # put orders (priority to sell orders to make profit right now)
        sortByProfit(will_be_sold, dict_eval_sell, self.wallet)
        for symbol in will_be_sold:
            profit = profitForSell(symbol, dict_eval_sell, self.wallet)
            if profit > 0:
                from_curr = getFromCurrency(symbol)
                sell_order = self.order_maker.makeOrder(symbol,
                                                        dict_eval_sell[symbol].price,
                                                        Side.SELL,
                                                        self.wallet.amount_for_currency(from_curr))
                if sell_order is not None:
                    sell_orders.append(sell_order)

        # buy by priority depending on proba
        sortByProba(buyable_now, dict_eval_buy)
        sortByProba(cannot_buy, dict_eval_buy)

        for symbol in buyable_now:
            to_curr = getToCurrency(symbol)
            buy_order = self.order_maker.makeOrder(symbol,
                                                   dict_eval_buy[symbol].price,
                                                   Side.BUY,
                                                   self.wallet.amount_for_currency(to_curr))
            if buy_order is not None:
                buy_orders.append(buy_order)

        return buy_orders, sell_orders

    def execute_orders(self):
        self.order_maker.printOrders()
        self.order_maker.executeOrders()
