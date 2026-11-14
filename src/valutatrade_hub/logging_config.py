
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from valutatrade_hub.infra.settings import SettingsLoader


def setup_logging():
    """Настроить журналирование с параметрами из конфигурации."""
    settings = SettingsLoader()

    logs_folder = Path(settings.get("logs_dir", "logs"))
    logs_folder.mkdir(parents=True, exist_ok=True)

    log_format = settings.get(
        "log_format",
        "%(asctime)s | %(levelname)s | %(message)s",
    )

    log_files = {
        "valutatrade_hub.actions": "actions.log",
        "valutatrade_hub.parser": "parser.log",
    }

    for logger_name, file_name in log_files.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

        if logger.handlers:
            continue

        handler = RotatingFileHandler(
            logs_folder / file_name,
            maxBytes=1_000_000,
            backupCount=3,
            encoding="utf-8",
        )

        handler.setFormatter(
            logging.Formatter(log_format)
        )

        logger.addHandler(handler)
        logger.propagate = False
