
class Wallet:
    def __init__(self, currency_code):
        self.currency_code = currency_code
        self._balance = 0.0

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Неверная сумма")

        self._balance += amount

    def withdraw(self, amount):
        self._balance -= amount

    def get_balance_info(self):
        return f"{self.currency_code}: {self._balance}"
