import time

from valutatrade_hub.core.exceptions import ApiRequestError
from valutatrade_hub.parser_service.updater import RatesUpdater


def run_scheduler(interval=300):
    """Обновлять курсы каждые interval секунд."""
    if interval <= 0:
        raise ValueError("Интервал должен быть больше нуля")

    print("Автообновление курсов запущено. Для остановки нажмите Ctrl+C.")

    try:
        while True:
            try:
                count = RatesUpdater().run_update()
                print(f"Обновлено курсов: {count}")
            except ApiRequestError as error:
                print(f"Не удалось обновить курсы: {error}")

            time.sleep(interval)
    except KeyboardInterrupt:
        print("Автообновление остановлено")


if __name__ == "__main__":
    run_scheduler()
