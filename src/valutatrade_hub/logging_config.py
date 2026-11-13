
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging():
    logs_folder = Path("logs")
    logs_folder.mkdir(exist_ok=True)

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
            logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s"
            )
        )

        logger.addHandler(handler)
        logger.propagate = False
