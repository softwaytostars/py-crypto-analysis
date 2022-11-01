from unittest import TestCase

from Model import Side
from algo.OrderMaker import OrderMaker
from Wallet import Wallet


class TestOrderMaker(TestCase):
    def test_make_order(self):
        wallet = Wallet()
        wallet.add_to_wallet_without_origin('BTC', 1.13)
        wallet.add_to_wallet_without_origin('EUR', 2000)
        ordermaker = OrderMaker(wallet, {'BINANCE_TAX_PERCENT': 0})
        ordermaker.makeOrder('BTCEUR', 8000, Side.SELL, 1)
        self.assertEqual(wallet.mean_cost_origin('BTC'), 0)
        self.assertEqual(wallet.mean_cost_origin('EUR'), 0)
        self.assertEqual(wallet.amount_for_currency('BTC'), 1.13)
        self.assertEqual(wallet.amount_for_currency('EUR'), 2000)

        ordermaker.executeOrders()

        self.assertEqual(0, wallet.mean_cost_origin('BTC'))
        self.assertEqual(8000, wallet.mean_cost_origin('EUR'))
        self.assertEqual(0.1299999999999999, wallet.amount_for_currency('BTC'))
        self.assertEqual(10000, wallet.amount_for_currency('EUR'))

