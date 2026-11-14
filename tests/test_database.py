
import json
from copy import deepcopy
from pathlib import Path


class DatabaseManager:
    """Единый менеджер JSON-хранилища (Singleton)."""

    _instance = None

    def __new__(cls):
        # __new__ гарантирует один экземпляр менеджера.
        if cls._instance is None:
            cls._instance = super().__new__(cls)

        return cls._instance

    def load(self, file_path, default=None):
        """Загрузить данные из JSON-файла."""
        path = Path(file_path)

        if not path.exists():
            return deepcopy(default)

        with path.open("r", encoding="utf-8-sig") as file:
            return json.load(file)

    def save(self, file_path, data):
        """Безопасно сохранить данные через временный файл."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        temp_path = path.with_name(f"{path.name}.tmp")

        try:
            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(
                    data,
                    file,
                    ensure_ascii=False,
                    indent=4,
                )

            temp_path.replace(path)

        finally:
            temp_path.unlink(missing_ok=True)
