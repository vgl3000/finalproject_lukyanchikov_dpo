
import json
from pathlib import Path

USERS_FILE = Path("data/users.json")


def load_users():
    if not USERS_FILE.exists():
        return []

    with open(USERS_FILE, "r", encoding="utf-8-sig") as file:
        users = json.load(file)

    return users


def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=4)
