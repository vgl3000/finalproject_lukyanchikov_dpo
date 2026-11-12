
import json
from pathlib import Path

SESSION_FILE = Path("data/session.json")


def save_session(username):
    session = {"username": username}

    with open(SESSION_FILE, "w", encoding="utf-8") as file:
        json.dump(session, file, ensure_ascii=False, indent=4)


def load_session():
    if not SESSION_FILE.exists():
        return None

    with open(SESSION_FILE, "r", encoding="utf-8") as file:
        session = json.load(file)

    return session["username"]
