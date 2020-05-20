from unittest import TestCase

from Wallet import Wallet
from simulator.Simulator import Simulator


class TestSimulator(TestCase):
    def test_simulatorBTCUSDT(self):
        simulator = Simulator(['BTCUSDT'])
        wallet = Wallet()
        wallet.addToWalletWithoutOrigin('USDT', 1)
        # wallet.addToWalletWithoutOrigin('BTC', 1)
        result = simulator.runSimu(wallet)
        self.assertTrue(1.266 < result[0] < 1.267)
        self.assertTrue(3.054 < result[1] < 3.055)
        self.assertTrue(2.039 < result[2] < 2.040)

    def test_simulatorETHUSDT(self):
        simulator = Simulator(['ETHUSDT'])
        wallet = Wallet()
        wallet.addToWalletWithoutOrigin('USDT', 1)
        # wallet.addToWalletWithoutOrigin('BTC', 1)
        result = simulator.runSimu(wallet)
        self.assertTrue(2.39 < result[0] < 2.4)
        self.assertTrue(2.24 < result[1] < 2.25)
        self.assertTrue(2.48 < result[2] < 2.49)