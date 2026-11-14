
# ValutaTrade Hub

Итоговый учебный проект на Python — платформа для отслеживания курсов фиатных и криптовалют и симуляции торговли через командную строку (CLI).

**Автор:** Лукьянчиков

Проект работает с виртуальными балансами. Реальные деньги и криптовалюты в операциях не используются.

## Возможности

- Регистрация и вход пользователя.
- Хранение пользователей и виртуальных портфелей в JSON.
- Пополнение виртуального USD-кошелька.
- Покупка и продажа валют за USD.
- Просмотр балансов и стоимости портфеля.
- Получение актуальных курсов и автоматическое обновление устаревшего кеша.
- Загрузка курсов через CoinGecko и ExchangeRate-API.
- Просмотр таблицы курсов с фильтрацией.
- Сохранение истории обновлений курсов.
- Логирование операций и ошибок.
- Проверка программы автоматическими тестами.

## Технологии

- Python 3.12+
- uv — управление проектом и зависимостями
- requests — HTTP-запросы
- PrettyTable — таблицы в терминале
- Ruff — проверка качества кода
- unittest — автоматические тесты

## Установка и запуск

Для работы нужны Python 3.12+ и uv.

Откройте терминал PowerShell в папке проекта и установите зависимости:

```powershell
uv sync
```

Проверьте доступные команды:

```powershell
uv run finalproject-lukyanchikov-dpo --help
```

Команды выполняются из корневой папки проекта.

## Поддерживаемые валюты

Фиатные валюты: USD, EUR, GBP, RUB.

Криптовалюты: BTC, ETH, SOL.

Для получения курсов используется USD как промежуточная базовая валюта.

## Примеры использования CLI

### 1. Регистрация

```powershell
uv run finalproject-lukyanchikov-dpo register --username demo --password 1234
```

### 2. Вход

```powershell
uv run finalproject-lukyanchikov-dpo login --username demo --password 1234
```

После входа имя пользователя сохраняется в локальном файле сессии.

**Примечание:** пароль `1234` предназначен только для учебного примера. При передаче пароля через аргумент командной строки он может сохраняться в истории терминала.

### 3. Пополнение виртуального баланса

```powershell
uv run finalproject-lukyanchikov-dpo deposit --amount 10000
```

Команда начисляет 10 000 виртуальных USD.

### 4. Обновление курсов

```powershell
uv run finalproject-lukyanchikov-dpo update-rates
```

Можно обновить только один источник:

```powershell
uv run finalproject-lukyanchikov-dpo update-rates --source coingecko
```

```powershell
uv run finalproject-lukyanchikov-dpo update-rates --source exchangerate
```

### 5. Покупка валюты

```powershell
uv run finalproject-lukyanchikov-dpo buy --currency EUR --amount 10
```

Программа рассчитывает стоимость покупки по текущему курсу и списывает виртуальные USD.

### 6. Продажа валюты

```powershell
uv run finalproject-lukyanchikov-dpo sell --currency EUR --amount 5
```

Программа уменьшает EUR-баланс и начисляет виртуальные USD.

### 7. Просмотр портфеля

```powershell
uv run finalproject-lukyanchikov-dpo show-portfolio
```

Оценка портфеля в EUR:

```powershell
uv run finalproject-lukyanchikov-dpo show-portfolio --base EUR
```

### 8. Получение курса

```powershell
uv run finalproject-lukyanchikov-dpo get-rate --from BTC --to USD
```

Обратная пара:

```powershell
uv run finalproject-lukyanchikov-dpo get-rate --from USD --to BTC
```

При отсутствии свежего курса программа пытается автоматически обновить данные через соответствующий API.

### 9. Таблица курсов

```powershell
uv run finalproject-lukyanchikov-dpo show-rates
```

Фильтр по валюте:

```powershell
uv run finalproject-lukyanchikov-dpo show-rates --currency BTC
```

Две самые дорогие криптовалюты из кеша:

```powershell
uv run finalproject-lukyanchikov-dpo show-rates --top 2
```

Отображение курсов в EUR:

```powershell
uv run finalproject-lukyanchikov-dpo show-rates --base EUR
```

## Parser Service и внешние API

Для криптовалют используется CoinGecko.

Для фиатных валют используется ExchangeRate-API.

В проекте предусмотрен запрос к бесплатному публичному API без ключа. Для работы с API необходим доступ к интернету.

При наличии API-ключей их можно передать через переменные окружения PowerShell:

```powershell
$env:COINGECKO_DEMO_API_KEY = "your_key"
$env:EXCHANGERATE_API_KEY = "your_key"
```

Замените `your_key` на собственный ключ. Ключи не следует записывать в исходный код или отправлять в GitHub.

## Кеширование и TTL

Полученные курсы сохраняются в `data/rates.json`.

В `pyproject.toml`, в разделе `[tool.valutatrade]`, задаётся срок актуальности кеша:

```toml
rates_ttl_seconds = 300
```

По умолчанию курс считается свежим в течение 300 секунд (5 минут).

При запросе отсутствующего или устаревшего курса торговые операции и команда `get-rate` пытаются обновить его автоматически. Если внешний API недоступен, операция может завершиться ошибкой.

Перед просмотром портфеля рекомендуется обновить курсы командой `update-rates`.

## Структура проекта

```text
finalproject_lukyanchikov_dpo/
├── data/
│   ├── users.json
│   ├── portfolios.json
│   ├── rates.json
│   └── exchange_rates.json
├── src/
│   └── valutatrade_hub/
│       ├── cli/
│       │   └── interface.py
│       ├── core/
│       │   ├── currencies.py
│       │   ├── exceptions.py
│       │   ├── models.py
│       │   ├── rates.py
│       │   └── usecases.py
│       ├── infra/
│       │   ├── database.py
│       │   ├── settings.py
│       │   ├── session.py
│       │   └── storage.py
│       ├── parser_service/
│       │   ├── api_clients.py
│       │   ├── config.py
│       │   ├── storage.py
│       │   └── updater.py
│       ├── decorators.py
│       └── logging_config.py
├── tests/
├── pyproject.toml
├── uv.lock
└── README.md
```

Пользователи и портфели сохраняются в JSON-файлах.

История полученных курсов хранится в `data/exchange_rates.json`.

Логи торговых операций записываются в `logs/actions.log`, а логи обновления курсов — в `logs/parser.log`.

## Архитектура

В проекте используются принципы объектно-ориентированного программирования:

- `Currency` — абстрактный базовый класс валюты.
- `FiatCurrency` и `CryptoCurrency` — наследники класса валюты.
- `User`, `Wallet`, `Portfolio` — модели предметной области.
- `SettingsLoader` — Singleton для настроек.
- `DatabaseManager` — Singleton для JSON-хранилища.
- `BaseApiClient` — абстракция API-клиента.
- `CoinGeckoClient` и `ExchangeRateApiClient` — реализации клиентов.
- `RatesUpdater` — обновление и сохранение курсов.
- `log_action` — декоратор логирования операций.

CLI находится отдельно от бизнес-логики.

## Тестирование

Запуск всех автоматических тестов:

```powershell
uv run python -m unittest discover -s tests -v
```

Проверка Ruff:

```powershell
uv run ruff check .
```

В текущем наборе предусмотрены 33 теста, проверяющие модели, валюты, исключения, Singleton, операции с балансами, автоматическое обновление курсов и обработку ответов API.

Сетевые запросы в автоматических тестах заменяются имитациями.

## Примеры ошибок

Недостаточно средств:

```text
Ошибка: Недостаточно средств: доступно 50 USD, требуется 100 USD
```

Неизвестная валюта:

```text
Ошибка: Неизвестная валюта 'ZZZ'
```

При ошибках подключения к API программа выводит сообщение и предлагает проверить интернет или повторить запрос позже.

## Назначение проекта

ValutaTrade Hub разработан как учебная симуляция торговли валютами.

Приложение не является биржей, не исполняет реальные финансовые операции и не предназначено для хранения реальных денежных средств.
