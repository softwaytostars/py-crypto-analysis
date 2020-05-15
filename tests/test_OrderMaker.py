from unittest import TestCase

from Model import Side
from OrderMaker import OrderMaker
from Wallet import Wallet


class TestOrderMaker(TestCase):
    def test_make_order(self):
        wallet = Wallet()
        wallet.addToWalletWithoutOrigin('BTC', 1.13)
        wallet.addToWalletWithoutOrigin('EUR', 2000)
        ordermaker = OrderMaker(wallet)
        ordermaker.makeOrder('BTCEUR', 8000, Side.SELL, 1)
        self.assertEqual(wallet.meanCostOrigin('BTC'), 0)
        self.assertEqual(wallet.meanCostOrigin('EUR'), 0)
        self.assertEqual(wallet.amountForCurrency('BTC'), 1.13)
        self.assertEqual(wallet.amountForCurrency('EUR'), 2000)

        ordermaker.executeOrders()

        self.assertEqual(0, wallet.meanCostOrigin('BTC'))
        self.assertEqual(8000, wallet.meanCostOrigin('EUR'))
        self.assertEqual(0.1299999999999999, wallet.amountForCurrency('BTC'))
        self.assertEqual(10000, wallet.amountForCurrency('EUR'))

