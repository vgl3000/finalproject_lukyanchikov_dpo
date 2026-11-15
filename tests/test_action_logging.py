import unittest
from unittest.mock import patch

from valutatrade_hub.decorators import log_action


class TestActionLogging(unittest.TestCase):
    def test_successful_buy_logging(self):
        def buy(username, currency_code, amount):
            return "Покупка выполнена"

        rates = {
            "pairs": {
                "EUR_USD": {
                    "rate": 1.2,
                }
            }
        }

        with (
            patch("valutatrade_hub.decorators.setup_logging"),
            patch(
                "valutatrade_hub.decorators.load_rates",
                return_value=rates,
            ),
            patch(
                "valutatrade_hub.decorators.logging.getLogger"
            ) as get_logger,
        ):
            result = log_action(buy)("demo", "EUR", 10)

        self.assertEqual(result, "Покупка выполнена")

        logger = get_logger.return_value
        args = logger.info.call_args.args
        message = args[0] % args[1:]

        self.assertIn("action=BUY", message)
        self.assertIn("user=demo", message)
        self.assertIn("currency=EUR", message)
        self.assertIn("amount=10", message)
        self.assertIn("rate=1.2", message)
        self.assertIn("base=USD", message)
        self.assertIn("result=OK", message)
        self.assertIn("timestamp=", message)

    def test_error_logging(self):
        def sell(username, currency_code, amount):
            raise ValueError("Неверная сумма")

        with (
            patch("valutatrade_hub.decorators.setup_logging"),
            patch(
                "valutatrade_hub.decorators.logging.getLogger"
            ) as get_logger,self.assertRaisesRegex(ValueError, "Неверная сумма")
        ):
            log_action(sell)("demo", "BTC", -5)

        logger = get_logger.return_value
        args = logger.error.call_args.args
        message = args[0] % args[1:]

        self.assertIn("action=SELL", message)
        self.assertIn("user=demo", message)
        self.assertIn("currency=BTC", message)
        self.assertIn("amount=-5", message)
        self.assertIn("result=ERROR", message)
        self.assertIn("error_type=ValueError", message)
        self.assertIn("error_message=Неверная сумма", message)

    def test_logging_without_cached_rate(self):
        def buy(username, currency_code, amount):
            return "OK"

        with (
            patch("valutatrade_hub.decorators.setup_logging"),
            patch(
                "valutatrade_hub.decorators.load_rates",
                return_value={"pairs": {}},
            ),
            patch(
                "valutatrade_hub.decorators.logging.getLogger"
            ) as get_logger,
        ):
            result = log_action(buy)("demo", "ETH", 1)

        self.assertEqual(result, "OK")

        args = get_logger.return_value.info.call_args.args
        message = args[0] % args[1:]

        self.assertIn("rate=-", message)


if __name__ == "__main__":
    unittest.main()