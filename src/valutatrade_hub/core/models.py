import hashlib
import math
import secrets
from datetime import datetime

from valutatrade_hub.core.currencies import get_currency
from valutatrade_hub.core.exceptions import InsufficientFundsError


def validate_amount(amount):
    """Проверить, что сумма положительная и конечная."""
    if type(amount) not in (int, float):
        raise ValueError("Сумма должна быть числом")

    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("Неверная сумма")


class Wallet:
    def __init__(self, currency_code):
        self.currency_code = currency_code
        self.balance = 0.0

    def deposit(self, amount):
        validate_amount(amount)

        self.balance += amount

    def withdraw(self, amount):
        validate_amount(amount)

        if amount > self.balance:
            raise InsufficientFundsError(
                "Недостаточно средств: "
                f"доступно {self.balance:g} {self.currency_code}, "
                f"требуется {amount:g} {self.currency_code}"
            )

        self.balance -= amount

    def get_balance_info(self):
        return f"{self.currency_code}: {self.balance}"

    @property
    def balance(self):
        return self._balance

    @balance.setter
    def balance(self, value):
        if type(value) not in (int, float):
            raise ValueError("Баланс должен быть числом")

        if not math.isfinite(value):
            raise ValueError("Баланс должен быть конечным числом")

        if value < 0:
            raise ValueError("Баланс не может быть отрицательным")

        self._balance = value


class User:
    def __init__(self, user_id, username, password):
        if not username.strip():
            raise ValueError("Имя не может быть пустым")

        if len(password) < 4:
            raise ValueError("Пароль слишком короткий")

        self._user_id = user_id
        self._username = username
        self._registration_date = datetime.now()

        self._salt = secrets.token_hex(8)
        self._hashed_password = hashlib.sha256(
            (password + self._salt).encode("utf-8")
        ).hexdigest()

    def get_user_info(self):
        return {
            "user_id": self._user_id,
            "username": self._username,
            "registration_date": self._registration_date.isoformat(),
        }

    def verify_password(self, password):
        password_hash = hashlib.sha256(
            (password + self._salt).encode("utf-8")
        ).hexdigest()

        return password_hash == self._hashed_password

    def change_password(self, new_password):
        if len(new_password) < 4:
            raise ValueError("Пароль слишком короткий")

        self._salt = secrets.token_hex(8)
        self._hashed_password = hashlib.sha256(
            (new_password + self._salt).encode("utf-8")
        ).hexdigest()

    def to_dict(self):
        return {
            "user_id": self._user_id,
            "username": self._username,
            "hashed_password": self._hashed_password,
            "salt": self._salt,
            "registration_date": self._registration_date.isoformat(),
        }


class Portfolio:
    def __init__(self, user):
        self._user = user
        self._wallets = {}

    def add_currency(self, currency_code):
        currency_code = get_currency(currency_code).code

        if currency_code in self._wallets:
            raise ValueError("Такой кошелёк уже есть")

        self._wallets[currency_code] = Wallet(currency_code)

    def get_wallet(self, currency_code):
        return self._wallets.get(currency_code)

    @property
    def user(self):
        return self._user

    @property
    def wallets(self):
        return self._wallets.copy()

    def get_total_value(self, base_currency="USD"):
        """Посчитать стоимость всех кошельков."""
        from valutatrade_hub.core.usecases import get_rate

        base_currency = get_currency(base_currency).code
        total = 0.0

        for code, wallet in self._wallets.items():
            if wallet.balance == 0:
                continue

            rate = get_rate(code, base_currency)
            total += wallet.balance * rate

        return total