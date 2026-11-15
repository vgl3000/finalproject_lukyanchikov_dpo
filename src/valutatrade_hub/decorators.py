import logging
from datetime import UTC, datetime
from functools import wraps

from valutatrade_hub.infra.storage import load_rates
from valutatrade_hub.logging_config import setup_logging


def log_action(func):
    """Записать информацию о торговой операции в журнал."""

    @wraps(func)
    def wrapper(username, currency_code, amount):
        setup_logging()
        logger = logging.getLogger("valutatrade_hub.actions")

        action = func.__name__.upper()
        code = str(currency_code).strip().upper()

        try:
            result = func(username, currency_code, amount)

            # После успешной сделки читаем курс из кеша.
            rate = "-"

            try:
                data = load_rates()
                pair = data.get("pairs", {}).get(f"{code}_USD")

                if isinstance(pair, dict):
                    rate = pair.get("rate", "-")

            except (OSError, ValueError, TypeError):
                pass

            logger.info(
                "timestamp=%s action=%s user=%s currency=%s "
                "amount=%s rate=%s base=USD result=OK",
                datetime.now(UTC).isoformat(),
                action,
                username,
                code,
                amount,
                rate,
            )

            return result

        except Exception as error:
            logger.error(
                "timestamp=%s action=%s user=%s currency=%s "
                "amount=%s base=USD result=ERROR "
                "error_type=%s error_message=%s",
                datetime.now(UTC).isoformat(),
                action,
                username,
                code,
                amount,
                type(error).__name__,
                str(error),
            )

            raise

    return wrapper