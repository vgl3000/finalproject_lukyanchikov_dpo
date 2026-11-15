
import unittest

from valutatrade_hub.core.models import Wallet


class TestWalletValidation(unittest.TestCase):
    def test_deposit_nan_rejected(self):
        wallet = Wallet("USD")

        with self.assertRaises(ValueError):
            wallet.deposit(float("nan"))

        self.assertEqual(wallet.balance, 0)

    def test_deposit_infinity_rejected(self):
        wallet = Wallet("USD")

        with self.assertRaises(ValueError):
            wallet.deposit(float("inf"))

        self.assertEqual(wallet.balance, 0)

    def test_withdraw_nan_rejected(self):
        wallet = Wallet("USD")
        wallet.deposit(100)

        with self.assertRaises(ValueError):
            wallet.withdraw(float("nan"))

        self.assertEqual(wallet.balance, 100)

    def test_invalid_balance_rejected(self):
        wallet = Wallet("USD")

        with self.assertRaises(ValueError):
            wallet.balance = float("inf")

        with self.assertRaises(ValueError):
            wallet.balance = float("nan")

        self.assertEqual(wallet.balance, 0)

    def test_balance_overflow_rejected(self):
        wallet = Wallet("USD")
        wallet.deposit(1e308)

        with self.assertRaises(ValueError):
            wallet.deposit(1e308)

        self.assertEqual(wallet.balance, 1e308)


if __name__ == "__main__":
    unittest.main()
