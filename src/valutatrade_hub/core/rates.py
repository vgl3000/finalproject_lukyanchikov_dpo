
import math

from valutatrade_hub.infra.storage import load_rates


def get_cached_rates(currency=None, top=None, base="USD"):
    data = load_rates()
    pairs = data.get("pairs", {})

    if not pairs:
        raise ValueError("Кеш пуст. Выполните update-rates")

    base = base.strip().upper()
    base_rate = 1.0

    if base != "USD":
        base_pair = pairs.get(f"{base}_USD")

        if base_pair is None:
            raise ValueError(f"Нет курса для {base}")

        base_rate = base_pair["rate"]

        if type(base_rate) not in (int, float):
            raise ValueError("Неверное значение курса")

        if not math.isfinite(base_rate) or base_rate <= 0:
            raise ValueError("Неверное значение курса")

    if currency is not None:
        currency = currency.strip().upper()

    if top is not None and top <= 0:
        raise ValueError("Количество должно быть больше нуля")

    result = []

    for pair_name, info in pairs.items():
        if not pair_name.endswith("_USD"):
            continue

        code = pair_name[:-4]

        if currency is not None and code != currency:
            continue

        if top is not None and code not in ("BTC", "ETH", "SOL"):
            continue

        rate = info.get("rate")

        if type(rate) not in (int, float):
            continue

        if not math.isfinite(rate) or rate <= 0:
            continue

        converted_rate = rate / base_rate

        result.append((
            code,
            converted_rate,
            info.get("source", "-"),
            info.get("updated_at", "-"),
        ))

    if not result:
        raise ValueError("Курсы по выбранному фильтру не найдены")

    if top is not None:
        result.sort(key=lambda item: item[1], reverse=True)
        result = result[:top]
    else:
        result.sort()

    return result, data.get("last_refresh")
