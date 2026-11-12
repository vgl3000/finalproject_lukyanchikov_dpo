
import argparse

from valutatrade_hub.core.usecases import (
    buy,
    get_portfolio_total,
    get_rate,
    get_user_portfolio,
    login,
    register,
    sell,
)
from valutatrade_hub.infra.session import load_session, save_session
from valutatrade_hub.parser_service.api_clients import ApiRequestError
from valutatrade_hub.parser_service.updater import RatesUpdater


def run():
    parser = argparse.ArgumentParser(
        description="ValutaTrade Hub"
    )

    commands = parser.add_subparsers(dest="command")

    register_command = commands.add_parser("register")
    register_command.add_argument("--username", required=True)
    register_command.add_argument("--password", required=True)

    login_command = commands.add_parser("login")
    login_command.add_argument("--username", required=True)
    login_command.add_argument("--password", required=True)

    portfolio_command = commands.add_parser("show-portfolio")
    portfolio_command.add_argument("--base", default="USD")

    rate_command = commands.add_parser("get-rate")
    rate_command.add_argument("--from", dest="from_currency", required=True)
    rate_command.add_argument("--to", required=True)

    buy_command = commands.add_parser("buy")
    buy_command.add_argument("--currency", required=True)
    buy_command.add_argument("--amount", type=float, required=True)

    sell_command = commands.add_parser("sell")
    sell_command.add_argument("--currency", required=True)
    sell_command.add_argument("--amount", type=float, required=True)

    update_command = commands.add_parser("update-rates")
    update_command.add_argument(
        "--source",
        choices=["coingecko", "exchangerate"],
    )

    args = parser.parse_args()

    try:
        if args.command == "register":
            result = register(args.username, args.password)
            print(result)

        elif args.command == "login":
            result = login(args.username, args.password)
            save_session(args.username)
            print(result)

        elif args.command == "show-portfolio":
            username = load_session()

            if username is None:
                raise ValueError("Сначала выполните login")

            portfolio = get_user_portfolio(username)
            total = get_portfolio_total(username, args.base)
            base_currency = args.base.upper()

            print(f"Портфель пользователя '{username}':")

            if not portfolio["wallets"]:
                print("Кошельков пока нет")
            else:
                for code, wallet in portfolio["wallets"].items():
                    print(f"{code}: {wallet['balance']}")

            print(f"ИТОГО: {total:.2f} {base_currency}")

        elif args.command == "get-rate":
            from_code = args.from_currency.strip().upper()
            to_code = args.to.strip().upper()

            rate = get_rate(from_code, to_code)
            reverse_rate = get_rate(to_code, from_code)

            print("Курсы из локального кеша:")
            print(f"Курс {from_code} -> {to_code}: {rate:.8f}")
            print(f"Обратный курс {to_code} -> {from_code}: {reverse_rate:.8f}")

        elif args.command == "buy":
            username = load_session()

            if username is None:
                raise ValueError("Сначала выполните login")

            result = buy(username, args.currency, args.amount)
            print(result)

        elif args.command == "sell":
            username = load_session()

            if username is None:
                raise ValueError("Сначала выполните login")

            result = sell(username, args.currency, args.amount)
            print(result)

        elif args.command == "update-rates":
            updater = RatesUpdater(args.source)
            count = updater.run_update()

            print(f"Обновлено курсов: {count}")

        else:
            parser.print_help()

    except (ValueError, ApiRequestError) as error:
        print(f"Ошибка: {error}")
