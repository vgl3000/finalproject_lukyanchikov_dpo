
import unittest
from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, call, patch

from valutatrade_hub.core.exceptions import (
    ApiRequestError,
    CurrencyNotFoundError,
)
from valutatrade_hub.core.usecases import get_rate


def make_rate(value, expired=False):
    """Создать тестовую запись курса."""
    updated_at = datetime.now(UTC)

    if expired:
        updated_at -= timedelta(hours=1)

    return {
        "rate": value,
        "updated_at": updated_at.isoformat(),
    }


class TestRatesRefresh(unittest.TestCase):
    def test_fresh_rate_does_not_call_api(self):
        """Свежий курс не требует обновления."""
        data = {
            "pairs": {
                "EUR_USD": make_rate(1.1),
            }
        }

        with (
            patch(
                "valutatrade_hub.core.usecases.load_rates",
                return_value=data,
            ),
            patch(
                "valutatrade_hub.parser_service.updater.RatesUpdater"
            ) as updater,
        ):
            result = get_rate("EUR", "USD")

        self.assertAlmostEqual(result, 1.1)
        updater.assert_not_called()

    def test_expired_crypto_rate_is_refreshed(self):
        """Устаревший BTC обновляется через CoinGecko."""
        data = {
            "pairs": {
                "BTC_USD": make_rate(50000, expired=True),
            }
        }

        def fake_refresh():
            data["pairs"]["BTC_USD"] = make_rate(60000)
            return 1

        with (
            patch(
                "valutatrade_hub.core.usecases.load_rates",
                return_value=data,
            ),
            patch(
                "valutatrade_hub.parser_service.updater.RatesUpdater"
            ) as updater,
        ):
            updater.return_value.run_update.side_effect = fake_refresh

            result = get_rate("BTC", "USD")

        self.assertAlmostEqual(result, 60000)
        updater.assert_called_once_with("coingecko")

    def test_missing_fiat_rate_is_refreshed(self):
        """Отсутствующий EUR обновляется через ExchangeRate."""
        data = {"pairs": {}}

        def fake_refresh():
            data["pairs"]["EUR_USD"] = make_rate(1.2)
            return 1

        with (
            patch(
                "valutatrade_hub.core.usecases.load_rates",
                return_value=data,
            ),
            patch(
                "valutatrade_hub.parser_service.updater.RatesUpdater"
            ) as updater,
        ):
            updater.return_value.run_update.side_effect = fake_refresh

            result = get_rate("EUR", "USD")

        self.assertAlmostEqual(result, 1.2)
        updater.assert_called_once_with("exchangerate")

    def test_two_missing_rates_use_two_sources(self):
        """Для BTC и EUR используются оба API."""
        data = {"pairs": {}}

        def fake_updater(source):
            instance = Mock()

            def fake_refresh():
                if source == "coingecko":
                    data["pairs"]["BTC_USD"] = make_rate(60000)
                elif source == "exchangerate":
                    data["pairs"]["EUR_USD"] = make_rate(1.2)

                return 1

            instance.run_update.side_effect = fake_refresh
            return instance

        with (
            patch(
                "valutatrade_hub.core.usecases.load_rates",
                return_value=data,
            ),
            patch(
                "valutatrade_hub.parser_service.updater.RatesUpdater",
                side_effect=fake_updater,
            ) as updater,
        ):
            result = get_rate("BTC", "EUR")

        self.assertAlmostEqual(result, 50000)
        self.assertEqual(
            updater.call_args_list,
            [
                call("coingecko"),
                call("exchangerate"),
            ],
        )

    def test_api_error_is_propagated(self):
        """Ошибка API передаётся вызывающей программе."""
        data = {"pairs": {}}

        with (
            patch(
                "valutatrade_hub.core.usecases.load_rates",
                return_value=data,
            ),
            patch(
                "valutatrade_hub.parser_service.updater.RatesUpdater"
            ) as updater,
        ):
            updater.return_value.run_update.side_effect = (
                ApiRequestError("Нет соединения")
            )

            with self.assertRaises(ApiRequestError):
                get_rate("BTC", "USD")

    def test_unknown_currency_does_not_call_api(self):
        """Неизвестную валюту не пытаемся обновлять."""
        with patch(
            "valutatrade_hub.parser_service.updater.RatesUpdater"
        ) as updater, self.assertRaises(CurrencyNotFoundError):
            get_rate("ZZZ", "USD")

        updater.assert_not_called()


if __name__ == "__main__":
    unittest.main()
