
import tomllib
from pathlib import Path
from typing import Any


class SettingsLoader:
    """Единая точка доступа к настройкам проекта (Singleton)."""

    _instance = None

    def __new__(cls):
        # __new__ выбран для простой реализации Singleton.
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):
        if hasattr(self, "_settings"):
            return

        self._settings = {}
        self.reload()

    def reload(self):
        """Перезагрузить настройки из pyproject.toml."""
        settings = {
            "rates_ttl_seconds": 300,
            "default_base_currency": "USD",
            "data_dir": "data",
            "users_file": "data/users.json",
            "portfolios_file": "data/portfolios.json",
            "rates_file": "data/rates.json",
            "history_file": "data/exchange_rates.json",
            "logs_dir": "logs",
            "log_format": (
                "%(asctime)s | %(levelname)s | %(message)s"
            ),
        }

        project_root = Path(__file__).resolve().parents[3]
        config_path = project_root / "pyproject.toml"

        if config_path.exists():
            with config_path.open("rb") as file:
                config = tomllib.load(file)

            custom_settings = (
                config.get("tool", {}).get("valutatrade", {})
            )
            settings.update(custom_settings)

        self._settings = settings

    def get(self, key: str, default: Any = None) -> Any:
        """Получить настройку по ключу."""
        return self._settings.get(key, default)
