
import argparse

from valutatrade_hub.core.usecases import (
    get_portfolio_total,
    get_user_portfolio,
    login,
    register,
)
from valutatrade_hub.infra.session import load_session, save_session


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

        else:
            parser.print_help()

    except ValueError as error:
        print(f"Ошибка: {error}")
