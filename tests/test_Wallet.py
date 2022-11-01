from unittest import TestCase

from Wallet import Wallet


class TestWallet(TestCase):
    def test_add_to_wallet_without_origin(self):
        wallet = Wallet()
        wallet.add_to_wallet_without_origin('BTC', 0.13)
        self.assertEqual(wallet.mean_cost_origin('BTC'), 0)
        self.assertEqual(wallet.amount_for_currency('BTC'), 0.13)

    def test_add_to_wallet_with_origin(self):
        wallet = Wallet()
        wallet.add_to_wallet_with_origin('BTC', 'BTCEUR', 6000, 0.003)
        self.assertEqual(wallet.amount_for_currency('BTC'), 0.003)

    def test_remove_from_wallet(self):
        wallet = Wallet()
        wallet.add_to_wallet_with_origin('BTC', 'BTCEUR', 6000, 0.003)
        wallet.remove_from_wallet('BTC', 0.001)
        self.assertEqual(0.002, wallet.amount_for_currency('BTC'))
        wallet.remove_from_wallet('BTC', 0.002)
        self.assertEqual(wallet.amount_for_currency('BTC'), 0)

    def test_mean_cost_origin(self):
        wallet = Wallet()
        wallet.add_to_wallet_with_origin('BTC', 'BTCEUR', 3000, 1)
        wallet.add_to_wallet_with_origin('BTC', 'BTCEUR', 7000, 3)
        self.assertEqual(wallet.mean_cost_origin('BTC'), 6000)

    def test_copy(self):
        wallet = Wallet()
        wallet.add_to_wallet_with_origin('BTC', 'BTCEUR', 3000, 1)
        wallet.add_to_wallet_without_origin('EUR', 2000)
        copy = wallet.copy()
        amountbtc = wallet.amount_for_currency('BTC')
        amounteur = wallet.amount_for_currency('EUR')
        meancostEur = wallet.mean_cost_origin('EUR')
        meancostBtc = wallet.mean_cost_origin('BTC')

        wallet.add_to_wallet_with_origin('BTC', 'BTCEUR', 30, 1000)
        wallet.add_to_wallet_without_origin('EUR', 200)

        self.assertEqual(amountbtc, copy.amount_for_currency('BTC'))
        self.assertEqual(amounteur, copy.amount_for_currency('EUR'))
        self.assertEqual(meancostEur, copy.mean_cost_origin('EUR'))
        self.assertEqual(meancostBtc, copy.mean_cost_origin('BTC'))
