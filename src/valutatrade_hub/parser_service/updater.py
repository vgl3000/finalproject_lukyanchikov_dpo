
from datetime import UTC, datetime

from valutatrade_hub.infra.storage import load_rates, save_rates
from valutatrade_hub.parser_service.api_clients import (
    ApiRequestError,
    CoinGeckoClient,
    ExchangeRateApiClient,
)


class RatesUpdater:
    def __init__(self):
        self.clients = [
            CoinGeckoClient(),
            ExchangeRateApiClient(),
        ]

    def run_update(self):
        data = load_rates()
        pairs = data.get("pairs", {})
        updated_at = datetime.now(UTC).isoformat()
        count = 0

        for client in self.clients:
            try:
                rates = client.fetch_rates()

                for code, rate in rates.items():
                    pairs[code] = {
                        "rate": rate,
                        "updated_at": updated_at,
                        "source": client.__class__.__name__,
                    }
                    count += 1

                print(f"{client.__class__.__name__}: OK")

            except ApiRequestError as error:
                print(f"Ошибка: {error}")

        if count == 0:
            raise ApiRequestError("Не удалось обновить курсы")

        data["pairs"] = pairs
        data["last_refresh"] = updated_at

        save_rates(data)

        return count
