
import logging
from functools import wraps

from valutatrade_hub.logging_config import setup_logging


def log_action(func):
    @wraps(func)
    def wrapper(username, currency_code, amount):
        setup_logging()
        logger = logging.getLogger("valutatrade_hub.actions")

        try:
            result = func(username, currency_code, amount)

            logger.info(
                "action=%s user=%s currency=%s amount=%s outcome=OK",
                func.__name__,
                username,
                currency_code,
                amount,
            )

            return result

        except Exception as error:
            logger.error(
                "action=%s user=%s currency=%s amount=%s outcome=ERROR error=%s",
                func.__name__,
                username,
                currency_code,
                amount,
                type(error).__name__,
            )
            raise

    return wrapper
