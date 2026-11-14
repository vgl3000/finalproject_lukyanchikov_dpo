
import math
from abc import ABC, abstractmethod

from valutatrade_hub.core.exceptions import CurrencyNotFoundError


class Currency(ABC):
    """Абстрактный базовый класс валюты."""

    def __init__(self, code: str, name: str):
        if (
            not isinstance(code, str)
            or not 2 <= len(code) <= 5
            or not code.isascii()
            or not code.isalnum()
        ):
            raise ValueError("Код валюты должен содержать 2–5 символов")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Название валюты не может быть пустым")

        self.code = code.upper()
        self.name = name.strip()

    @abstractmethod
    def get_display_info(self) -> str:
        """Вернуть информацию о валюте."""

    def __str__(self) -> str:
        return self.get_display_info()


class FiatCurrency(Currency):
    """Фиатная валюта."""

    def __init__(self, code: str, name: str, issuing_country: str):
        super().__init__(code, name)

        if (
            not isinstance(issuing_country, str)
            or not issuing_country.strip()
        ):
            raise ValueError("Страна выпуска не может быть пустой")

        self.issuing_country = issuing_country.strip()

    def get_display_info(self) -> str:
        return (
            f"[FIAT] {self.code} — {self.name} "
            f"(Issuing: {self.issuing_country})"
        )

    def get_info(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
            "type": "fiat",
            "issuing_country": self.issuing_country,
        }


class CryptoCurrency(Currency):
    """Криптовалюта."""

    def __init__(
        self,
        code: str,
        name: str,
        algorithm: str,
        market_cap: float,
    ):
        super().__init__(code, name)

        if not isinstance(algorithm, str) or not algorithm.strip():
            raise ValueError("Алгоритм не может быть пустым")

        if (
            type(market_cap) not in (int, float)
            or not math.isfinite(market_cap)
            or market_cap < 0
        ):
            raise ValueError("Капитализация должна быть неотрицательным числом")

        self.algorithm = algorithm.strip()
        self.market_cap = float(market_cap)

    def get_display_info(self) -> str:
        cap = f"{self.market_cap:.2e}".replace("e+", "e")

        return (
            f"[CRYPTO] {self.code} — {self.name} "
            f"(Algo: {self.algorithm}, MCAP: {cap})"
        )

    def get_info(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
            "type": "crypto",
            "algorithm": self.algorithm,
            "market_cap": self.market_cap,
        }


# Капитализация здесь демонстрационная, а не актуальная рыночная.
CURRENCY_REGISTRY = {
    "USD": ("fiat", "US Dollar", "United States"),
    "EUR": ("fiat", "Euro", "Eurozone"),
    "GBP": ("fiat", "British Pound", "United Kingdom"),
    "RUB": ("fiat", "Russian Ruble", "Russia"),
    "BTC": ("crypto", "Bitcoin", "SHA-256", 1.12e12),
    "ETH": ("crypto", "Ethereum", "Proof of Stake", 0.0),
    "SOL": ("crypto", "Solana", "Proof of Stake", 0.0),
}


def get_currency(code: str) -> Currency:
    """Создать объект валюты по коду из реестра."""
    if not isinstance(code, str):
        raise CurrencyNotFoundError(f"Неизвестная валюта '{code}'")

    normalized_code = code.upper()
    data = CURRENCY_REGISTRY.get(normalized_code)

    if data is None:
        raise CurrencyNotFoundError(
            f"Неизвестная валюта '{normalized_code}'"
        )

    if data[0] == "fiat":
        return FiatCurrency(
            normalized_code,
            data[1],
            data[2],
        )

    return CryptoCurrency(
        normalized_code,
        data[1],
        data[2],
        data[3],
    )
