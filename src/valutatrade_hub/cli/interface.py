
import argparse

from valutatrade_hub.core.usecases import register


def run():
    parser = argparse.ArgumentParser(
        description="ValutaTrade Hub"
    )

    commands = parser.add_subparsers(dest="command")

    register_command = commands.add_parser("register")
    register_command.add_argument("--username", required=True)
    register_command.add_argument("--password", required=True)

    args = parser.parse_args()

    if args.command == "register":
        try:
            result = register(args.username, args.password)
            print(result)
        except ValueError as error:
            print(f"Ошибка: {error}")
    else:
        parser.print_help()
