
import unittest

from valutatrade_hub.core.exceptions import InsufficientFundsError
from valutatrade_hub.core.models import Wallet


class TestWalletErrors(unittest.TestCase):
    def test_insufficient_usd_message(self):
        wallet = Wallet("USD")
        wallet.deposit(50)

        with self.assertRaises(InsufficientFundsError) as context:
            wallet.withdraw(100)

        self.assertEqual(
            str(context.exception),
            "Недостаточно средств: доступно 50 USD, "
            "требуется 100 USD",
        )
        self.assertEqual(wallet.balance, 50)

    def test_insufficient_eur_message(self):
        wallet = Wallet("EUR")
        wallet.deposit(2.5)

        with self.assertRaises(InsufficientFundsError) as context:
            wallet.withdraw(3.75)

        self.assertEqual(
            str(context.exception),
            "Недостаточно средств: доступно 2.5 EUR, "
            "требуется 3.75 EUR",
        )
        self.assertEqual(wallet.balance, 2.5)


if __name__ == "__main__":
    unittest.main()
