from unittest import TestCase

from Wallet import Wallet


class TestWallet(TestCase):
    def test_add_to_wallet_without_origin(self):
        wallet = Wallet()
        wallet.addToWalletWithoutOrigin('BTC', 0.13)
        self.assertEqual(wallet.meanCostOrigin('BTC'), 0)
        self.assertEqual(wallet.amountForCurrency('BTC'), 0.13)

    def test_add_to_wallet_with_origin(self):
        wallet = Wallet()
        wallet.addToWalletWithOrigin('BTC', 'BTCEUR', 6000, 0.003)
        self.assertEqual(wallet.amountForCurrency('BTC'), 0.003)

    def test_remove_from_wallet(self):
        wallet = Wallet()
        wallet.addToWalletWithOrigin('BTC', 'BTCEUR', 6000, 0.003)
        wallet.removeFromWallet('BTC', 0.001)
        self.assertEqual(0.002, wallet.amountForCurrency('BTC'))
        wallet.removeFromWallet('BTC', 0.002)
        self.assertEqual(wallet.amountForCurrency('BTC'), 0)

    def test_mean_cost_origin(self):
        wallet = Wallet()
        wallet.addToWalletWithOrigin('BTC', 'BTCEUR', 3000, 1)
        wallet.addToWalletWithOrigin('BTC', 'BTCEUR', 7000, 3)
        self.assertEqual(wallet.meanCostOrigin('BTC'), 6000)

    def test_copy(self):
        wallet = Wallet()
        wallet.addToWalletWithOrigin('BTC', 'BTCEUR', 3000, 1)
        wallet.addToWalletWithoutOrigin('EUR', 2000)
        copy = wallet.copy()
        amountbtc = wallet.amountForCurrency('BTC')
        amounteur = wallet.amountForCurrency('EUR')
        meancostEur = wallet.meanCostOrigin('EUR')
        meancostBtc = wallet.meanCostOrigin('BTC')

        wallet.addToWalletWithOrigin('BTC', 'BTCEUR', 30, 1000)
        wallet.addToWalletWithoutOrigin('EUR', 200)

        self.assertEqual(amountbtc, copy.amountForCurrency('BTC'))
        self.assertEqual(amounteur, copy.amountForCurrency('EUR'))
        self.assertEqual(meancostEur, copy.meanCostOrigin('EUR'))
        self.assertEqual(meancostBtc, copy.meanCostOrigin('BTC'))

