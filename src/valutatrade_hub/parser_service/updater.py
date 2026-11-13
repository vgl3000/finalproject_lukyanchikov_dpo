
import logging
from datetime import UTC, datetime

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.infra.storage import load_rates, save_rates
from valutatrade_hub.logging_config import setup_logging
from valutatrade_hub.parser_service.api_clients import (
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
        setup_logging()
        logger = logging.getLogger("valutatrade_hub.parser")

        data = load_rates()
        pairs = data.get("pairs", {})

        updated_at = datetime.now(UTC).isoformat()
        new_records = []
        count = 0

        logger.info("action=update_rates status=START")

        for client in self.clients:
            source = client.__class__.__name__

            try:
                rates = client.fetch_rates()

                for pair_name, rate in rates.items():
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

                logger.info(
                    "source=%s status=OK count=%s",
                    source,
                    len(rates),
                )

                print(f"{source}: OK")

            except ApiRequestError as error:
                logger.error(
                    "source=%s status=ERROR error=%s",
                    source,
                    error,
                )

                print(f"Ошибка: {error}")

        if count == 0:
            logger.error(
                "action=update_rates status=ERROR count=0"
            )
            raise ApiRequestError("Не удалось обновить курсы")

        data["pairs"] = pairs
        data["last_refresh"] = updated_at

        save_rates(data)
        save_history(new_records)

        logger.info(
            "action=update_rates status=OK total=%s",
            count,
        )

        return count
