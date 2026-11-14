
import math
from abc import ABC, abstractmethod

import requests

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.config import ParserConfig


class BaseApiClient(ABC):
    @abstractmethod
    def fetch_rates(self):
        """Получить курсы валют из API."""


class CoinGeckoClient(BaseApiClient):
    def fetch_rates(self):
        config = ParserConfig()

        params = {
            "ids": ",".join(config.CRYPTO_ID_MAP.values()),
            "vs_currencies": "usd",
        }

        headers = {}

        if config.coingecko_key:
            headers["x-cg-demo-api-key"] = config.coingecko_key

        try:
            response = requests.get(
                config.COINGECKO_URL,
                params=params,
                headers=headers,
                timeout=config.TIMEOUT,
            )

            response.raise_for_status()
            data = response.json()

        except (requests.RequestException, ValueError) as error:
            raise ApiRequestError(
                "Ошибка при обращении к внешнему API: "
                "не удалось получить курсы CoinGecko"
            ) from error

        if not isinstance(data, dict):
            raise ApiRequestError(
                "Ошибка при обращении к внешнему API: "
                "CoinGecko вернул неверный формат данных"
            )

        rates = {}

        for code, coin_id in config.CRYPTO_ID_MAP.items():
            coin_data = data.get(coin_id)

            if not isinstance(coin_data, dict):
                continue

            rate = coin_data.get("usd")

            if type(rate) not in (int, float):
                continue

            if not math.isfinite(rate) or rate <= 0:
                continue

            rates[f"{code}_USD"] = float(rate)

        if not rates:
            raise ApiRequestError(
                "Ошибка при обращении к внешнему API: "
                "CoinGecko не вернул корректных курсов"
            )

        return rates


class ExchangeRateApiClient(BaseApiClient):
    def fetch_rates(self):
        config = ParserConfig()

        url = config.EXCHANGERATE_FREE_URL
        headers = {}

        if config.exchangerate_key:
            url = config.EXCHANGERATE_URL
            headers["Authorization"] = (
                f"Bearer {config.exchangerate_key}"
            )

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=config.TIMEOUT,
            )

            response.raise_for_status()
            data = response.json()

        except (requests.RequestException, ValueError) as error:
            raise ApiRequestError(
                "Ошибка при обращении к внешнему API: "
                "не удалось получить курсы ExchangeRate-API"
            ) from error

        if not isinstance(data, dict):
            raise ApiRequestError(
                "Ошибка при обращении к внешнему API: "
                "ExchangeRate-API вернул неверный формат данных"
            )

        if data.get("result") != "success":
            reason = data.get(
                "error-type",
                "неизвестная ошибка",
            )

            raise ApiRequestError(
                "Ошибка при обращении к внешнему API: "
                f"ExchangeRate-API ({reason})"
            )

        conversion_rates = data.get("conversion_rates")

        if conversion_rates is None:
            conversion_rates = data.get("rates")

        if not isinstance(conversion_rates, dict):
            raise ApiRequestError(
                "Ошибка при обращении к внешнему API: "
                "ExchangeRate-API не вернул таблицу курсов"
            )

        rates = {}

        for code in config.FIAT_CODES:
            value = conversion_rates.get(code)

            if type(value) not in (int, float):
                continue

            if not math.isfinite(value) or value <= 0:
                continue

            # API возвращает стоимость USD в данной валюте.
            # Нам нужна обратная стоимость валюты в USD.
            rates[f"{code}_USD"] = 1 / value

        if not rates:
            raise ApiRequestError(
                "Ошибка при обращении к внешнему API: "
                "ExchangeRate-API не вернул корректных курсов"
            )

        return rates
