
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
