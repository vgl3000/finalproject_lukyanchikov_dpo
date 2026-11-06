
import hashlib
import secrets
from datetime import datetime


class Wallet:
    def __init__(self, currency_code):
        self.currency_code = currency_code
        self._balance = 0.0

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Неверная сумма")

        self._balance += amount

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Неверная сумма")

        if amount > self._balance:
            raise ValueError("Недостаточно денег")

        self._balance -= amount

    def get_balance_info(self):
        return f"{self.currency_code}: {self._balance}"

    @property
    def balance(self):
        return self._balance


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


class Portfolio:
    def __init__(self, user):
        self._user = user
        self._wallets = {}

    def add_currency(self, currency_code):
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
        exchange_rates = {
            "USD": 1.0,
            "EUR": 1.1,
            "BTC": 60000.0,
        }

        if base_currency not in exchange_rates:
            raise ValueError("Неизвестная валюта")

        total_usd = 0.0

        for code, wallet in self._wallets.items():
            if code not in exchange_rates:
                raise ValueError("Неизвестная валюта")

            total_usd += wallet.balance * exchange_rates[code]

        return total_usd / exchange_rates[base_currency]
