
from datetime import UTC, datetime

from valutatrade_hub.infra.storage import load_rates, save_rates
from valutatrade_hub.parser_service.api_clients import (
    ApiRequestError,
    CoinGeckoClient,
    ExchangeRateApiClient,
)
from valutatrade_hub.parser_service.storage import save_history


class RatesUpdater:
    def __init__(self, source=None):
        if source == "coingecko":
            self.clients = [CoinGeckoClient()]

        elif source == "exchangerate":
            self.clients = [ExchangeRateApiClient()]

        else:
            self.clients = [
                CoinGeckoClient(),
                ExchangeRateApiClient(),
            ]

    def run_update(self):
        data = load_rates()
        pairs = data.get("pairs", {})

        updated_at = datetime.now(UTC).isoformat()
        new_records = []
        count = 0

        for client in self.clients:
            try:
                rates = client.fetch_rates()

                for pair_name, rate in rates.items():
                    source = client.__class__.__name__

                    pairs[pair_name] = {
                        "rate": rate,
                        "updated_at": updated_at,
                        "source": source,
                    }

                    currency_code = pair_name.removesuffix("_USD")

                    record = {
                        "id": f"{pair_name}_{updated_at}",
                        "from_currency": currency_code,
                        "to_currency": "USD",
                        "rate": rate,
                        "timestamp": updated_at,
                        "source": source,
                    }

                    new_records.append(record)
                    count += 1

                print(f"{client.__class__.__name__}: OK")

            except ApiRequestError as error:
                print(f"Ошибка: {error}")

        if count == 0:
            raise ApiRequestError("Не удалось обновить курсы")

        data["pairs"] = pairs
        data["last_refresh"] = updated_at

        save_rates(data)
        save_history(new_records)

        return count
