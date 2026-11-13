
class InsufficientFundsError(ValueError):
    """Ошибка: недостаточно средств."""


class CurrencyNotFoundError(ValueError):
    """Ошибка: валюта или её курс не найдены."""


class ApiRequestError(ValueError):
    """Ошибка получения данных от API."""
