import unittest
from unittest.mock import patch

from valutatrade_hub.parser_service.scheduler import run_scheduler


class TestScheduler(unittest.TestCase):
    def test_invalid_interval(self):
        with self.assertRaises(ValueError):
            run_scheduler(0)

    def test_one_update_and_stop(self):
        with (
            patch(
                "valutatrade_hub.parser_service.scheduler.RatesUpdater"
            ) as updater,
            patch(
                "valutatrade_hub.parser_service.scheduler.time.sleep",
                side_effect=KeyboardInterrupt,
            ),
        ):
            updater.return_value.run_update.return_value = 3
            run_scheduler(1)

        updater.return_value.run_update.assert_called_once()


if __name__ == "__main__":
    unittest.main()
