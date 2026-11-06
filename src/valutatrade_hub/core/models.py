
class Wallet:
    """Кошелёк для хранения одной валюты."""

    def __init__(self, currency_code: str):
        self.currency_code = currency_code
        self._balance = 0.0

    def deposit(self, amount: float):
        self._balance += amount

    def get_balance_info(self):
        return f"{self.currency_code}: {self._balance}"
