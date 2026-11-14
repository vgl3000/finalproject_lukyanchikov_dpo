
import hashlib
import math
from datetime import UTC, datetime

from valutatrade_hub.core.currencies import CryptoCurrency, get_currency
from valutatrade_hub.core.exceptions import CurrencyNotFoundError
from valutatrade_hub.core.models import User, Wallet
from valutatrade_hub.decorators import log_action
from valutatrade_hub.infra.settings import SettingsLoader
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
        "wallets": {},
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
    currency_code = get_currency(currency_code).code
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
    currency_code = get_currency(currency_code).code
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
    currency_code = get_currency(currency_code).code
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
    currency_code = get_currency(currency_code).code

    if currency_code == "USD":
        return 1.0

    data = load_rates()
    pairs = data.get("pairs", {})
    pair = pairs.get(f"{currency_code}_USD")

    if pair is None:
        raise CurrencyNotFoundError(
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

    ttl_seconds = SettingsLoader().get("rates_ttl_seconds")

    if age.total_seconds() > ttl_seconds:
        raise ValueError(
            f"Курс {currency_code} устарел. Выполните update-rates"
        )

    if type(rate) not in (int, float):
        raise ValueError("Неверное значение курса")

    if not math.isfinite(rate) or rate <= 0:
        raise ValueError("Неверное значение курса")

    return rate


def get_rate(from_code, to_code):
    """Получить курс и при необходимости обновить кеш."""
    from_code = get_currency(from_code).code
    to_code = get_currency(to_code).code

    usd_rates = {}
    missing_or_expired = []

    # Проверяем обе валюты, не запрашивая одну валюту дважды.
    for code in dict.fromkeys((from_code, to_code)):
        try:
            usd_rates[code] = get_usd_rate(code)

        except CurrencyNotFoundError as error:
            if not str(error).startswith("Нет курса для "):
                raise

            missing_or_expired.append(code)

        except ValueError as error:
            if "устарел" not in str(error):
                raise

            missing_or_expired.append(code)

    if missing_or_expired:
        # Локальный импорт позволяет избежать циклических импортов.
        from valutatrade_hub.parser_service.updater import RatesUpdater

        sources = []

        for code in missing_or_expired:
            currency = get_currency(code)

            if isinstance(currency, CryptoCurrency):
                source = "coingecko"
            else:
                source = "exchangerate"

            if source not in sources:
                sources.append(source)

        # Запрашиваем только необходимые источники курсов.
        for source in sources:
            RatesUpdater(source).run_update()

        # После обновления повторно читаем данные из кеша.
        for code in missing_or_expired:
            usd_rates[code] = get_usd_rate(code)

    return usd_rates[from_code] / usd_rates[to_code]


def get_portfolio_total(username, base_currency="USD"):
    base_currency = get_currency(base_currency).code
    portfolio = get_user_portfolio(username)

    total_usd = 0.0

    for code, wallet in portfolio["wallets"].items():
        rate = get_usd_rate(code)
        total_usd += wallet["balance"] * rate

    base_rate = get_usd_rate(base_currency)

    return total_usd / base_rate


@log_action
def buy(username, currency_code, amount):
    currency_code = get_currency(currency_code).code

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
    currency_code = get_currency(currency_code).code

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


def deposit_usd(username, amount):
    """Пополнить виртуальный USD-кошелёк пользователя."""
    if type(amount) not in (int, float):
        raise ValueError("Сумма должна быть числом")

    if not math.isfinite(amount) or amount <= 0:
        raise ValueError("Сумма должна быть положительным числом")

    user_id = get_user_portfolio(username)["user_id"]
    portfolios = load_portfolios()

    for portfolio in portfolios:
        if portfolio["user_id"] == user_id:
            wallets = portfolio["wallets"]
            wallet = Wallet("USD")

            if "USD" in wallets:
                wallet.balance = wallets["USD"]["balance"]

            wallet.deposit(amount)

            wallets["USD"] = {
                "currency_code": "USD",
                "balance": wallet.balance,
            }

            save_portfolios(portfolios)

            return (
                f"Пополнено {amount:.2f} виртуальных USD. "
                f"Баланс: {wallet.balance:.2f} USD"
            )

    raise ValueError("Портфель не найден")
