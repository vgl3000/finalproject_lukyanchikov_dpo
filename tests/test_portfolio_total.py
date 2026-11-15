import unittest
from datetime import UTC, datetime, timedelta
from unittest.mock import patch

from valutatrade_hub.core.usecases import get_portfolio_total


class TestPortfolioTotal(unittest.TestCase):
    def test_total_with_expired_rate(self):
        old_date = datetime.now(UTC) - timedelta(hours=1)

        rates = {
            "pairs": {
                "EUR_USD": {
                    "rate": 1.1,
                    "updated_at": old_date.isoformat(),
                }
            }
        }

        portfolio = {
            "wallets": {
                "USD": {"balance": 100},
                "EUR": {"balance": 10},
            }
        }

        def refresh_rates():
            rates["pairs"]["EUR_USD"] = {
                "rate": 1.2,
                "updated_at": datetime.now(UTC).isoformat(),
            }
            return 1

        with (
            patch(
                "valutatrade_hub.core.usecases.get_user_portfolio",
                return_value=portfolio,
            ),
            patch(
                "valutatrade_hub.core.usecases.load_rates",
                return_value=rates,
            ),
            patch(
                "valutatrade_hub.parser_service.updater.RatesUpdater"
            ) as updater,
        ):
            updater.return_value.run_update.side_effect = refresh_rates

            total = get_portfolio_total("demo")

        self.assertAlmostEqual(total, 112)
        updater.assert_called_once_with("exchangerate")

    def test_total_in_another_currency(self):
        portfolio = {
            "wallets": {
                "EUR": {"balance": 10},
                "GBP": {"balance": 5},
            }
        }

        def fake_get_rate(from_code, to_code):
            if from_code == "EUR" and to_code == "GBP":
                return 0.8

            return 1.0

        with (
            patch(
                "valutatrade_hub.core.usecases.get_user_portfolio",
                return_value=portfolio,
            ),
            patch(
                "valutatrade_hub.core.usecases.get_rate",
                side_effect=fake_get_rate,
            ),
        ):
            total = get_portfolio_total("demo", "GBP")

        self.assertAlmostEqual(total, 13)

    def test_empty_portfolio(self):
        portfolio = {"wallets": {}}

        with (
            patch(
                "valutatrade_hub.core.usecases.get_user_portfolio",
                return_value=portfolio,
            ),
            patch(
                "valutatrade_hub.core.usecases.get_rate"
            ) as get_rate_mock,
        ):
            total = get_portfolio_total("demo")

        self.assertEqual(total, 0)
        get_rate_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()