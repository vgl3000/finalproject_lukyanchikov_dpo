
import argparse

from valutatrade_hub.core.usecases import login, register


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

    args = parser.parse_args()

    try:
        if args.command == "register":
            result = register(args.username, args.password)
            print(result)

        elif args.command == "login":
            result = login(args.username, args.password)
            print(result)

        else:
            parser.print_help()

    except ValueError as error:
        print(f"Ошибка: {error}")
