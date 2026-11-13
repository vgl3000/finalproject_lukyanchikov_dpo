
class Currency:
    def __init__(self, code, name):
        if not isinstance(code, str) or not code.strip():
            raise ValueError("Код валюты не может быть пустым")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Название валюты не может быть пустым")

        self.code = code.strip().upper()
        self.name = name.strip()

    def __str__(self):
        return f"{self.code} — {self.name}"


class FiatCurrency(Currency):
    def __init__(self, code, name, country):
        super().__init__(code, name)

        if not isinstance(country, str) or not country.strip():
            raise ValueError("Страна не может быть пустой")

        self.country = country.strip()

    def get_info(self):
        return {
            "code": self.code,
            "name": self.name,
            "type": "fiat",
            "country": self.country,
        }


class CryptoCurrency(Currency):
    def __init__(self, code, name, blockchain):
        super().__init__(code, name)

        if not isinstance(blockchain, str) or not blockchain.strip():
            raise ValueError("Блокчейн не может быть пустым")

        self.blockchain = blockchain.strip()

    def get_info(self):
        return {
            "code": self.code,
            "name": self.name,
            "type": "crypto",
            "blockchain": self.blockchain,
        }
