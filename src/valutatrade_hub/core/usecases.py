
import hashlib

from valutatrade_hub.core.models import User, Wallet
from valutatrade_hub.infra.storage import (
    load_portfolios,
    load_users,
    save_portfolios,
    save_users,
)


def register(username, password):
    users = load_users()
    portfolios = load_portfolios()

    for user in users:
        if user["username"] == username:
            raise ValueError("Такое имя уже занято")

    new_id = 1

    for user in users:
        if user["user_id"] >= new_id:
            new_id = user["user_id"] + 1

    new_user = User(new_id, username, password)
    users.append(new_user.to_dict())

    new_portfolio = {
        "user_id": new_id,
        "wallets": {}
    }

    portfolios.append(new_portfolio)

    save_users(users)
    save_portfolios(portfolios)

    return f"Пользователь {username} зарегистрирован"


def login(username, password):
    users = load_users()

    for user in users:
        if user["username"] == username:
            password_hash = hashlib.sha256(
                (password + user["salt"]).encode("utf-8")
            ).hexdigest()

            if password_hash != user["hashed_password"]:
                raise ValueError("Неверный пароль")

            return f"Вы вошли как '{username}'"

    raise ValueError("Пользователь не найден")


def get_portfolio(user_id):
    portfolios = load_portfolios()

    for portfolio in portfolios:
        if portfolio["user_id"] == user_id:
            return portfolio

    raise ValueError("Портфель не найден")


def add_currency(user_id, currency_code):
    if not isinstance(currency_code, str) or not currency_code.strip():
        raise ValueError("Неверный код валюты")

    currency_code = currency_code.strip().upper()
    portfolios = load_portfolios()

    for portfolio in portfolios:
        if portfolio["user_id"] == user_id:
            if currency_code in portfolio["wallets"]:
                raise ValueError("Такой кошелёк уже есть")

            wallet = Wallet(currency_code)

            portfolio["wallets"][currency_code] = {
                "currency_code": wallet.currency_code,
                "balance": wallet.balance,
            }

            save_portfolios(portfolios)
            return f"Кошелёк {currency_code} добавлен"

    raise ValueError("Портфель не найден")


def deposit_wallet(user_id, currency_code, amount):
    if not isinstance(currency_code, str) or not currency_code.strip():
        raise ValueError("Неверный код валюты")

    currency_code = currency_code.strip().upper()
    portfolios = load_portfolios()

    for portfolio in portfolios:
        if portfolio["user_id"] == user_id:
            if currency_code not in portfolio["wallets"]:
                raise ValueError("Кошелёк не найден")

            wallet_data = portfolio["wallets"][currency_code]

            wallet = Wallet(currency_code)
            wallet.balance = wallet_data["balance"]
            wallet.deposit(amount)

            wallet_data["balance"] = wallet.balance
            save_portfolios(portfolios)

            return f"Баланс {currency_code}: {wallet.balance}"

    raise ValueError("Портфель не найден")


def withdraw_wallet(user_id, currency_code, amount):
    if not isinstance(currency_code, str) or not currency_code.strip():
        raise ValueError("Неверный код валюты")

    currency_code = currency_code.strip().upper()
    portfolios = load_portfolios()

    for portfolio in portfolios:
        if portfolio["user_id"] == user_id:
            if currency_code not in portfolio["wallets"]:
                raise ValueError("Кошелёк не найден")

            wallet_data = portfolio["wallets"][currency_code]

            wallet = Wallet(currency_code)
            wallet.balance = wallet_data["balance"]
            wallet.withdraw(amount)

            wallet_data["balance"] = wallet.balance
            save_portfolios(portfolios)

            return f"Баланс {currency_code}: {wallet.balance}"

    raise ValueError("Портфель не найден")
