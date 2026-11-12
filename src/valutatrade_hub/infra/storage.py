
import json
from pathlib import Path

USERS_FILE = Path("data/users.json")
PORTFOLIOS_FILE = Path("data/portfolios.json")
RATES_FILE = Path("data/rates.json")


def load_users():
    if not USERS_FILE.exists():
        return []

    with open(USERS_FILE, "r", encoding="utf-8-sig") as file:
        users = json.load(file)

    return users


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=4)


def load_portfolios():
    if not PORTFOLIOS_FILE.exists():
        return []

    with open(PORTFOLIOS_FILE, "r", encoding="utf-8-sig") as file:
        portfolios = json.load(file)

    return portfolios


def save_portfolios(portfolios):
    with open(PORTFOLIOS_FILE, "w", encoding="utf-8") as file:
        json.dump(portfolios, file, ensure_ascii=False, indent=4)


def load_rates():
    if not RATES_FILE.exists():
        return {"pairs": {}, "last_refresh": None}

    with open(RATES_FILE, "r", encoding="utf-8-sig") as file:
        rates = json.load(file)

    return rates


def save_rates(rates):
    RATES_FILE.parent.mkdir(parents=True, exist_ok=True)

    temp_file = RATES_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(rates, file, ensure_ascii=False, indent=4)

    temp_file.replace(RATES_FILE)
