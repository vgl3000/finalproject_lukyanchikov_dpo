
import os


class ParserConfig:
    COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"

    EXCHANGERATE_URL = "https://v6.exchangerate-api.com/v6/latest/USD"
    EXCHANGERATE_FREE_URL = "https://open.er-api.com/v6/latest/USD"

    TIMEOUT = 10

    FIAT_CODES = ("EUR", "GBP", "RUB")

    def __init__(self):
        self.coingecko_key = os.getenv("COINGECKO_DEMO_API_KEY", "")
        self.exchangerate_key = os.getenv("EXCHANGERATE_API_KEY", "")

        self.CRYPTO_ID_MAP = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "SOL": "solana",
        }
