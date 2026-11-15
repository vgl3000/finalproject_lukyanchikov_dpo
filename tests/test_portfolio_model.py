import unittest
from unittest.mock import patch

from valutatrade_hub.core.exceptions import CurrencyNotFoundError
from valutatrade_hub.core.models import Portfolio, User


class TestPortfolioModel(unittest.TestCase):
    def setUp(self):
        self.user = User(1, "demo", "1234")
        self.portfolio = Portfolio(self.user)

    def test_total_with_different_currencies(self):
        self.portfolio.add_currency("EUR")
        self.portfolio.add_currency("SOL")

        self.portfolio.get_wallet("EUR").deposit(10)
        self.portfolio.get_wallet("SOL").deposit(2)

        def fake_rate(from_code, to_code):
            rates = {
                "EUR": 1.2,
                "SOL": 150,
            }
            return rates[from_code]

        with patch(
            "valutatrade_hub.core.usecases.get_rate",
            side_effect=fake_rate,
        ):
            total = self.portfolio.get_total_value()

        self.assertAlmostEqual(total, 312)

    def test_empty_portfolio(self):
        with patch(
            "valutatrade_hub.core.usecases.get_rate"
        ) as rate_mock:
            total = self.portfolio.get_total_value()

        self.assertEqual(total, 0)
        rate_mock.assert_not_called()

    def test_unknown_currency(self):
        with self.assertRaises(CurrencyNotFoundError):
            self.portfolio.add_currency("ZZZ")

    def test_duplicate_currency(self):
        self.portfolio.add_currency("EUR")

        with self.assertRaises(ValueError):
            self.portfolio.add_currency("eur")


if __name__ == "__main__":
    unittest.main()