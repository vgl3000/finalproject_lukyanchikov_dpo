import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from valutatrade_hub.infra.session import SESSION_FILE
from valutatrade_hub.infra.storage import (
    PORTFOLIOS_FILE,
    RATES_FILE,
    USERS_FILE,
)
from valutatrade_hub.parser_service.storage import HISTORY_FILE


class TestFilePaths(unittest.TestCase):
    def test_paths_do_not_depend_on_current_folder(self):
        paths = [USERS_FILE, PORTFOLIOS_FILE, RATES_FILE,
                 SESSION_FILE, HISTORY_FILE]

        with TemporaryDirectory() as folder:
            old_folder = Path.cwd()

            try:
                os.chdir(folder)

                for path in paths:
                    self.assertTrue(path.is_absolute())
                    self.assertNotEqual(path.parent, Path(folder))
            finally:
                os.chdir(old_folder)


if __name__ == "__main__":
    unittest.main()
