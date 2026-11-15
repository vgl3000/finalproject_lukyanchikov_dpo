import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from valutatrade_hub.cli.interface import run


class TestCliRateTimestamp(unittest.TestCase):
    def test_get_rate_shows_update_time(self):
        rates = {
            "pairs": {
                "EUR_USD": {
                    "rate": 1.2,
                    "updated_at": "2026-11-15T12:00:00+00:00",
                }
            }
        }

        output = io.StringIO()

        with (
            patch(
                "sys.argv",
                ["program", "get-rate", "--from", "EUR", "--to", "USD"],
            ),
            patch(
                "valutatrade_hub.cli.interface.get_rate",
                side_effect=[1.2, 1 / 1.2],
            ),
            patch(
                "valutatrade_hub.cli.interface.load_rates",
                return_value=rates,
            ),
            redirect_stdout(output),
        ):
            run()

        result = output.getvalue()

        self.assertIn("Курс EUR → USD: 1.20000000", result)
        self.assertIn(
            "Обновлено: 2026-11-15T12:00:00+00:00",
            result,
        )


if __name__ == "__main__":
    unittest.main()