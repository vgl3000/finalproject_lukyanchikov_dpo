
from abc import ABC, abstractmethod

import requests

from valutatrade_hub.parser_service.config import ParserConfig


class ApiRequestError(Exception):
    pass


class BaseApiClient(ABC):
    @abstractmethod
    def fetch_rates(self):
        pass


class CoinGeckoClient(BaseApiClient):
    def fetch_rates(self):
        config = ParserConfig()

        coin_ids = ",".join(config.CRYPTO_ID_MAP.values())

        params = {
            "ids": coin_ids,
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
                "Не удалось получить курсы CoinGecko"
            ) from error

        rates = {}

        for code, coin_id in config.CRYPTO_ID_MAP.items():
            if coin_id in data and "usd" in data[coin_id]:
                rate = data[coin_id]["usd"]

                if type(rate) in (int, float) and rate > 0:
                    rates[f"{code}_USD"] = float(rate)

        if not rates:
            raise ApiRequestError("CoinGecko не вернул курсы")

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
                "Не удалось получить курсы ExchangeRate-API"
            ) from error

        if data.get("result") != "success":
            raise ApiRequestError("Ошибка ответа ExchangeRate-API")

        conversion_rates = data.get("conversion_rates", {})
        rates = {}

        for code in config.FIAT_CODES:
            if code in conversion_rates:
                value = conversion_rates[code]

                if type(value) in (int, float) and value > 0:
                    rates[f"{code}_USD"] = 1 / value

        if not rates:
            raise ApiRequestError("ExchangeRate-API не вернул курсы")

        return rates
