
import os
import unittest
from unittest.mock import Mock, patch

import requests

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.api_clients import (
    CoinGeckoClient,
    ExchangeRateApiClient,
)
from valutatrade_hub.parser_service.config import ParserConfig


def make_response(data):
    """Создать поддельный ответ API без интернета."""
    response = Mock()
    response.json.return_value = data
    return response


class TestCoinGeckoClient(unittest.TestCase):
    def test_successful_crypto_rates(self):
        data = {
            "bitcoin": {"usd": 60000},
            "ethereum": {"usd": 3000},
            "solana": {"usd": 150},
        }

        with (
            patch.dict(
                os.environ,
                {"COINGECKO_DEMO_API_KEY": ""},
            ),
            patch(
                "valutatrade_hub.parser_service.api_clients.requests.get",
                return_value=make_response(data),
            ) as request,
        ):
            rates = CoinGeckoClient().fetch_rates()

        self.assertEqual(rates["BTC_USD"], 60000.0)
        self.assertEqual(rates["ETH_USD"], 3000.0)
        self.assertEqual(rates["SOL_USD"], 150.0)

        self.assertEqual(
            request.call_args.kwargs["headers"],
            {},
        )

    def test_invalid_crypto_response(self):
        data = {
            "bitcoin": None,
            "ethereum": [],
            "solana": "invalid",
        }

        with patch(
            "valutatrade_hub.parser_service.api_clients.requests.get",
            return_value=make_response(data),
        ), self.assertRaisesRegex(
            ApiRequestError,
            "корректных курсов",
        ):
            CoinGeckoClient().fetch_rates()

    def test_coingecko_network_error(self):
        with patch(
            "valutatrade_hub.parser_service.api_clients.requests.get",
            side_effect=requests.Timeout("Timeout"),
        ), self.assertRaisesRegex(
            ApiRequestError,
            "не удалось получить курсы CoinGecko",
        ):
            CoinGeckoClient().fetch_rates()


class TestExchangeRateApiClient(unittest.TestCase):
    def test_free_api_success(self):
        data = {
            "result": "success",
            "rates": {
                "EUR": 0.8,
                "GBP": 0.75,
                "RUB": 90,
            },
        }

        with (
            patch.dict(
                os.environ,
                {"EXCHANGERATE_API_KEY": ""},
            ),
            patch(
                "valutatrade_hub.parser_service.api_clients.requests.get",
                return_value=make_response(data),
            ) as request,
        ):
            rates = ExchangeRateApiClient().fetch_rates()

        self.assertAlmostEqual(rates["EUR_USD"], 1.25)
        self.assertAlmostEqual(rates["GBP_USD"], 1 / 0.75)
        self.assertAlmostEqual(rates["RUB_USD"], 1 / 90)

        request.assert_called_once_with(
            ParserConfig.EXCHANGERATE_FREE_URL,
            headers={},
            timeout=ParserConfig.TIMEOUT,
        )

    def test_api_key_uses_bearer(self):
        data = {
            "result": "success",
            "conversion_rates": {
                "EUR": 0.8,
                "GBP": 0.75,
                "RUB": 90,
            },
        }

        with (
            patch.dict(
                os.environ,
                {"EXCHANGERATE_API_KEY": "demo-test-key"},
            ),
            patch(
                "valutatrade_hub.parser_service.api_clients.requests.get",
                return_value=make_response(data),
            ) as request,
        ):
            rates = ExchangeRateApiClient().fetch_rates()

        self.assertAlmostEqual(rates["EUR_USD"], 1.25)

        request.assert_called_once_with(
            ParserConfig.EXCHANGERATE_URL,
            headers={
                "Authorization": "Bearer demo-test-key",
            },
            timeout=ParserConfig.TIMEOUT,
        )

    def test_api_reports_invalid_key(self):
        data = {
            "result": "error",
            "error-type": "invalid-key",
        }

        with patch(
            "valutatrade_hub.parser_service.api_clients.requests.get",
            return_value=make_response(data),
        ), self.assertRaisesRegex(
            ApiRequestError,
            "invalid-key",
        ):
            ExchangeRateApiClient().fetch_rates()

    def test_invalid_rates_are_rejected(self):
        data = {
            "result": "success",
            "rates": {
                "EUR": float("nan"),
                "GBP": 0,
                "RUB": False,
            },
        }

        with patch(
            "valutatrade_hub.parser_service.api_clients.requests.get",
            return_value=make_response(data),
        ), self.assertRaisesRegex(
            ApiRequestError,
            "корректных курсов",
        ):
            ExchangeRateApiClient().fetch_rates()

    def test_invalid_json_structure(self):
        with patch(
            "valutatrade_hub.parser_service.api_clients.requests.get",
            return_value=make_response([]),
        ), self.assertRaisesRegex(
            ApiRequestError,
            "неверный формат данных",
        ):
            ExchangeRateApiClient().fetch_rates()


if __name__ == "__main__":
    unittest.main()
