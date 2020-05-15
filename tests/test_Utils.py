from unittest import TestCase

from Utils import sortByProba, sortByProfit
from Wallet import Wallet
from evaluators.Evaluation import Evaluation


class TestUtils(TestCase):
    def test_sortByProba(self):
        buyablenow = ['ETCBTC', 'BTCEUR', 'ETHEUR', 'BNBBTC']
        dictEvalBuy = {'ETCBTC': Evaluation(0.65, 0.15),
                       'BTCEUR': Evaluation(0.75, 0.15),
                       'ETHEUR': Evaluation(0.15, 0.15),
                       'BNBBTC': Evaluation(0.7, 0.15)}
        sortByProba(buyablenow, dictEvalBuy)
        self.assertEqual(buyablenow[0], 'BTCEUR')
        self.assertEqual(buyablenow[1], 'BNBBTC')
        self.assertEqual(buyablenow[2], 'ETCBTC')
        self.assertEqual(buyablenow[3], 'ETHEUR')

    def test_sortByProbaNoStock(self):
        buyablenow = []
        dictEvalBuy = {'ETCBTC': Evaluation(0.65, 0.15),
                       'BTCEUR': Evaluation(0.75, 0.15),
                       'ETHEUR': Evaluation(0.15, 0.15),
                       'BNBBTC': Evaluation(0.7, 0.15)}
        sortByProba(buyablenow, dictEvalBuy)
        self.assertEqual(len(buyablenow), 0)

    def test_sort_by_profit(self):
        sellable = ['ETCBTC', 'BTCEUR', 'ETHEUR', 'BNBBTC']
        dictEvalSell = {'ETCBTC': Evaluation(0.65, 0.15),
                        'BTCEUR': Evaluation(0.75, 0.15),
                        'ETHEUR': Evaluation(0.15, 0.15),
                        'BNBBTC': Evaluation(0.7, 0.15)}
        wallet = Wallet()
        wallet.addToWalletWithOrigin('ETC', 'ETCBTC', 0.05, 1)  # profit 0.1
        wallet.addToWalletWithOrigin('BTC', 'BTCEUR', 0.15, 1)  # profit 0
        wallet.addToWalletWithOrigin('ETH', 'ETHEUR', 0.01, 1)  # profit 0.14
        wallet.addToWalletWithOrigin('BNB', 'BNBBTC', 0.04, 1)  # profit 0.11

        sortByProfit(sellable, dictEvalSell, wallet)
        self.assertEqual(sellable[0], 'ETHEUR')
        self.assertEqual(sellable[1], 'BNBBTC')
        self.assertEqual(sellable[2], 'ETCBTC')
        self.assertEqual(sellable[3], 'BTCEUR')

    def test_getFromCurrency(self):
       # self.assertEqual(sellable[0], 'ETHEUR')
