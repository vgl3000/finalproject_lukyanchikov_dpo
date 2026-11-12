
import json
from pathlib import Path

HISTORY_FILE = Path("data/exchange_rates.json")


def load_history():
    if not HISTORY_FILE.exists():
        return []

    with open(HISTORY_FILE, "r", encoding="utf-8-sig") as file:
        return json.load(file)


def save_history(new_records):
    history = load_history()

    existing_ids = set()

    for record in history:
        existing_ids.add(record["id"])

    for record in new_records:
        if record["id"] not in existing_ids:
            history.append(record)
            existing_ids.add(record["id"])

    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)

    temp_file = HISTORY_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=4)

    temp_file.replace(HISTORY_FILE)
