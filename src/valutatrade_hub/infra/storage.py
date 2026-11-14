
from pathlib import Path

from valutatrade_hub.infra.database import DatabaseManager
from valutatrade_hub.infra.settings import SettingsLoader

settings = SettingsLoader()

USERS_FILE = Path(settings.get("users_file"))
PORTFOLIOS_FILE = Path(settings.get("portfolios_file"))
RATES_FILE = Path(settings.get("rates_file"))


def load_users():
    """Загрузить пользователей."""
    return DatabaseManager().load(USERS_FILE, [])


def save_users(users):
    """Сохранить пользователей."""
    DatabaseManager().save(USERS_FILE, users)


def load_portfolios():
    """Загрузить портфели."""
    return DatabaseManager().load(PORTFOLIOS_FILE, [])


def save_portfolios(portfolios):
    """Сохранить портфели."""
    DatabaseManager().save(PORTFOLIOS_FILE, portfolios)


def load_rates():
    """Загрузить кеш курсов."""
    return DatabaseManager().load(
        RATES_FILE,
        {"pairs": {}, "last_refresh": None},
    )


def save_rates(rates):
    """Сохранить кеш курсов."""
    DatabaseManager().save(RATES_FILE, rates)
