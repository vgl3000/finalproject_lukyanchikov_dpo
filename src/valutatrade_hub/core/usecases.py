
import hashlib
import math
from datetime import UTC, datetime

from valutatrade_hub.core.models import User, Wallet
from valutatrade_hub.decorators import log_action
from valutatrade_hub.infra.storage import (
    load_portfolios,
    load_rates,
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


def get_user_portfolio(username):
    users = load_users()

    for user in users:
        if user["username"] == username:
            return get_portfolio(user["user_id"])

    raise ValueError("Пользователь не найден")


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


def get_usd_rate(currency_code):
    if currency_code == "USD":
        return 1.0

    data = load_rates()
    pairs = data.get("pairs", {})
    pair = pairs.get(f"{currency_code}_USD")

    if pair is None:
        raise ValueError(
            f"Нет курса для {currency_code}. Выполните update-rates"
        )

    try:
        rate = pair["rate"]
        updated_at = datetime.fromisoformat(pair["updated_at"])

    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("Ошибка данных курса") from error

    if updated_at.tzinfo is None:
        raise ValueError("Ошибка времени обновления курса")

    age = datetime.now(UTC) - updated_at

    if age.total_seconds() > 300:
        raise ValueError(
            f"Курс {currency_code} устарел. Выполните update-rates"
        )

    if type(rate) not in (int, float):
        raise ValueError("Неверное значение курса")

    if not math.isfinite(rate) or rate <= 0:
        raise ValueError("Неверное значение курса")

    return rate


def get_rate(from_code, to_code):
    if not isinstance(from_code, str) or not from_code.strip():
        raise ValueError("Неверный код валюты")

    if not isinstance(to_code, str) or not to_code.strip():
        raise ValueError("Неверный код валюты")

    from_code = from_code.strip().upper()
    to_code = to_code.strip().upper()

    from_rate = get_usd_rate(from_code)
    to_rate = get_usd_rate(to_code)

    return from_rate / to_rate


def get_portfolio_total(username, base_currency="USD"):
    portfolio = get_user_portfolio(username)

    base_currency = base_currency.strip().upper()
    total_usd = 0.0

    for code, wallet in portfolio["wallets"].items():
        rate = get_usd_rate(code)
        total_usd += wallet["balance"] * rate

    base_rate = get_usd_rate(base_currency)

    return total_usd / base_rate


@log_action
def buy(username, currency_code, amount):
    if not isinstance(currency_code, str) or not currency_code.strip():
        raise ValueError("Неверный код валюты")

    currency_code = currency_code.strip().upper()

    if currency_code == "USD":
        raise ValueError("Нельзя купить USD за USD")

    if type(amount) not in (int, float) or not math.isfinite(amount):
        raise ValueError("Неверная сумма")

    if amount <= 0:
        raise ValueError("Неверная сумма")

    rate = get_rate(currency_code, "USD")
    cost = amount * rate

    if not math.isfinite(cost):
        raise ValueError("Неверная сумма")

    user_id = get_user_portfolio(username)["user_id"]
    portfolios = load_portfolios()

    for portfolio in portfolios:
        if portfolio["user_id"] == user_id:
            wallets = portfolio["wallets"]

            if "USD" not in wallets:
                raise ValueError("Сначала пополните USD-кошелёк")

            usd_wallet = Wallet("USD")
            usd_wallet.balance = wallets["USD"]["balance"]
            usd_wallet.withdraw(cost)

            currency_wallet = Wallet(currency_code)

            if currency_code in wallets:
                currency_wallet.balance = wallets[currency_code]["balance"]

            currency_wallet.deposit(amount)

            wallets["USD"]["balance"] = usd_wallet.balance
            wallets[currency_code] = {
                "currency_code": currency_code,
                "balance": currency_wallet.balance,
            }

            save_portfolios(portfolios)

            return f"Куплено {amount} {currency_code} за {cost:.2f} USD"

    raise ValueError("Портфель не найден")


@log_action
def sell(username, currency_code, amount):
    if not isinstance(currency_code, str) or not currency_code.strip():
        raise ValueError("Неверный код валюты")

    currency_code = currency_code.strip().upper()

    if currency_code == "USD":
        raise ValueError("Нельзя продать USD за USD")

    if type(amount) not in (int, float) or not math.isfinite(amount):
        raise ValueError("Неверная сумма")

    if amount <= 0:
        raise ValueError("Неверная сумма")

    rate = get_rate(currency_code, "USD")
    income = amount * rate

    if not math.isfinite(income):
        raise ValueError("Неверная сумма")

    user_id = get_user_portfolio(username)["user_id"]
    portfolios = load_portfolios()

    for portfolio in portfolios:
        if portfolio["user_id"] == user_id:
            wallets = portfolio["wallets"]

            if currency_code not in wallets:
                raise ValueError("Кошелёк не найден")

            currency_wallet = Wallet(currency_code)
            currency_wallet.balance = wallets[currency_code]["balance"]
            currency_wallet.withdraw(amount)

            usd_wallet = Wallet("USD")

            if "USD" in wallets:
                usd_wallet.balance = wallets["USD"]["balance"]

            usd_wallet.deposit(income)

            wallets[currency_code]["balance"] = currency_wallet.balance
            wallets["USD"] = {
                "currency_code": "USD",
                "balance": usd_wallet.balance,
            }

            save_portfolios(portfolios)

            return f"Продано {amount} {currency_code} за {income:.2f} USD"

    raise ValueError("Портфель не найден")
