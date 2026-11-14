
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from valutatrade_hub.infra.database import DatabaseManager
from valutatrade_hub.infra.storage import load_users, save_users


class TestDatabaseManager(unittest.TestCase):
    def test_singleton(self):
        first = DatabaseManager()
        second = DatabaseManager()

        self.assertIs(first, second)

    def test_json_read_write(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "data" / "test.json"
            database = DatabaseManager()

            self.assertEqual(database.load(path, []), [])

            expected = {
                "currency": "USD",
                "balance": 100,
            }

            database.save(path, expected)

            self.assertEqual(
                database.load(path, {}),
                expected,
            )

            self.assertFalse(
                path.with_name(f"{path.name}.tmp").exists()
            )

    def test_storage_uses_database_manager(self):
        with TemporaryDirectory() as folder:
            path = Path(folder) / "users.json"

            users = [
                {"user_id": 1, "username": "demo"}
            ]

            with patch(
                "valutatrade_hub.infra.storage.USERS_FILE",
                path,
            ):
                save_users(users)
                loaded_users = load_users()

            self.assertEqual(loaded_users, users)


if __name__ == "__main__":
    unittest.main()
