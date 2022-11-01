from unittest import TestCase

from simu.Simulator import Simulator
from Wallet import Wallet


class TestSimulator(TestCase):
    def test_simulatorBTCUSDT(self):
        # Create
        simulator = Simulator(['BTCUSDT'])
        wallet = Wallet()
        wallet.add_to_wallet_without_origin('USDT', 1)
        # wallet.add_to_wallet_without_origin('BTC', 1)
        result = simulator.run_simu(wallet)
        self.assertTrue(1.266 < result[0] < 1.267) # 2018
        self.assertTrue(3.054 < result[1] < 3.055) # 2019
        self.assertTrue(2.039 < result[2] < 2.040) # 2020

    def test_simulatorETHUSDT(self):
        simulator = Simulator(['ETHUSDT'])
        wallet = Wallet()
        wallet.add_to_wallet_without_origin('USDT', 1)
        # wallet.add_to_wallet_without_origin('BTC', 1)
        result = simulator.run_simu(wallet)
        self.assertTrue(2.39 < result[0] < 2.4)
        self.assertTrue(2.24 < result[1] < 2.25)
        self.assertTrue(2.48 < result[2] < 2.49)