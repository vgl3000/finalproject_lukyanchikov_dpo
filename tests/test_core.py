
import unittest
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from valutatrade_hub.core.currencies import (
    CryptoCurrency,
    FiatCurrency,
    get_currency,
)
from valutatrade_hub.core.exceptions import (
    CurrencyNotFoundError,
    InsufficientFundsError,
)
from valutatrade_hub.core.models import User, Wallet
from valutatrade_hub.core.usecases import (
    buy,
    deposit_usd,
    get_rate,
    get_usd_rate,
    sell,
)
from valutatrade_hub.infra.settings import SettingsLoader


class TestWallet(unittest.TestCase):
    def test_deposit_and_withdraw(self):
        wallet = Wallet("USD")
        wallet.deposit(100)
        wallet.withdraw(40)

        self.assertEqual(wallet.balance, 60)

    def test_insufficient_funds(self):
        wallet = Wallet("USD")

        with self.assertRaises(InsufficientFundsError):
            wallet.withdraw(100)

    def test_invalid_amount(self):
        wallet = Wallet("USD")

        with self.assertRaises(ValueError):
            wallet.deposit(-10)


class TestUser(unittest.TestCase):
    def test_password_hashing(self):
        user = User(1, "demo", "1234")

        self.assertTrue(user.verify_password("1234"))
        self.assertFalse(user.verify_password("wrong"))
        self.assertNotEqual(user.to_dict()["hashed_password"], "1234")

    def test_change_password(self):
        user = User(1, "demo", "1234")
        user.change_password("5678")

        self.assertFalse(user.verify_password("1234"))
        self.assertTrue(user.verify_password("5678"))


class TestCurrencies(unittest.TestCase):
    def test_fiat_currency(self):
        currency = get_currency("USD")

        self.assertIsInstance(currency, FiatCurrency)
        self.assertIn("[FIAT]", currency.get_display_info())

    def test_crypto_currency(self):
        currency = get_currency("BTC")

        self.assertIsInstance(currency, CryptoCurrency)
        self.assertIn("[CRYPTO]", currency.get_display_info())

    def test_unknown_currency(self):
        with self.assertRaises(CurrencyNotFoundError):
            get_currency("ZZZ")


class TestSettings(unittest.TestCase):
    def test_singleton(self):
        first = SettingsLoader()
        second = SettingsLoader()

        self.assertIs(first, second)
        self.assertEqual(first.get("rates_ttl_seconds"), 300)


class TestUsecases(unittest.TestCase):
    def test_usd_to_usd(self):
        self.assertEqual(get_rate("USD", "USD"), 1.0)

    def test_fresh_cached_rate(self):
        rates = {
            "pairs": {
                "EUR_USD": {
                    "rate": 1.1,
                    "updated_at": datetime.now(UTC).isoformat(),
                }
            }
        }

        with patch(
            "valutatrade_hub.core.usecases.load_rates",
            return_value=rates,
        ):
            self.assertAlmostEqual(get_usd_rate("EUR"), 1.1)

    def test_expired_cached_rate(self):
        old_date = datetime.now(UTC) - timedelta(hours=1)

        rates = {
            "pairs": {
                "EUR_USD": {
                    "rate": 1.1,
                    "updated_at": old_date.isoformat(),
                }
            }
        }

        with patch(
            "valutatrade_hub.core.usecases.load_rates",
            return_value=rates,
        ), self.assertRaisesRegex(ValueError, "устарел"):
            get_usd_rate("EUR")

    def test_deposit_usd(self):
        portfolios = [
            {"user_id": 7, "wallets": {}}
        ]

        with (
            patch(
                "valutatrade_hub.core.usecases.get_user_portfolio",
                return_value={"user_id": 7},
            ),
            patch(
                "valutatrade_hub.core.usecases.load_portfolios",
                return_value=portfolios,
            ),
            patch(
                "valutatrade_hub.core.usecases.save_portfolios"
            ) as save_mock,
        ):
            deposit_usd("demo", 1000)

        self.assertEqual(
            portfolios[0]["wallets"]["USD"]["balance"],
            1000,
        )
        save_mock.assert_called_once()

    def test_buy_and_sell(self):
        portfolios = [
            {
                "user_id": 7,
                "wallets": {
                    "USD": {
                        "currency_code": "USD",
                        "balance": 1000.0,
                    }
                },
            }
        ]

        with (
            patch(
                "valutatrade_hub.core.usecases.get_user_portfolio",
                return_value={"user_id": 7},
            ),
            patch(
                "valutatrade_hub.core.usecases.load_portfolios",
                return_value=portfolios,
            ),
            patch(
                "valutatrade_hub.core.usecases.save_portfolios"
            ) as save_mock,
            patch(
                "valutatrade_hub.core.usecases.get_rate",
                return_value=1.1,
            ),
        ):
            buy("demo", "EUR", 10)
            sell("demo", "EUR", 5)

        wallets = portfolios[0]["wallets"]

        self.assertAlmostEqual(wallets["EUR"]["balance"], 5)
        self.assertAlmostEqual(wallets["USD"]["balance"], 994.5)
        self.assertEqual(save_mock.call_count, 2)


if __name__ == "__main__":
    unittest.main()
