# Демонстрация работы проекта

Это план для записи терминала на защите. Все команды выполняются
в PowerShell из папки проекта. Вводите их по одной.

## 1. Подготовка

```powershell
uv sync
uv run ruff check .
uv run python -m unittest discover -s tests -v
```

Перед записью выберите новое имя пользователя, например `demo_student_2`.
Если имя уже зарегистрировано, замените его в следующих двух командах.

## 2. Работа с кошельком

Регистрация:

```powershell
uv run finalproject-lukyanchikov-dpo register --username demo_student_2 --password 1234
```

Вход:

```powershell
uv run finalproject-lukyanchikov-dpo login --username demo_student_2 --password 1234
```

Пополнение виртуального баланса:

```powershell
uv run finalproject-lukyanchikov-dpo deposit --amount 10000
```

Обновление курсов из двух API:

```powershell
uv run finalproject-lukyanchikov-dpo update-rates
```

Покупка и продажа:

```powershell
uv run finalproject-lukyanchikov-dpo buy --currency EUR --amount 10
uv run finalproject-lukyanchikov-dpo sell --currency EUR --amount 5
```

Просмотр портфеля:

```powershell
uv run finalproject-lukyanchikov-dpo show-portfolio
```

## 3. Курсы валют

```powershell
uv run finalproject-lukyanchikov-dpo get-rate --from EUR --to USD
uv run finalproject-lukyanchikov-dpo show-rates
uv run finalproject-lukyanchikov-dpo show-rates --top 2
```

Цифры зависят от актуальных курсов API и могут меняться.

## 4. Проверка ошибок

Попытка продать больше валюты, чем есть на счёте:

```powershell
uv run finalproject-lukyanchikov-dpo sell --currency EUR --amount 100
```

Программа должна вывести сообщение о недостатке средств.

Неизвестная валюта:

```powershell
uv run finalproject-lukyanchikov-dpo get-rate --from ZZZ --to USD
```

Программа должна сообщить, что валюта неизвестна.

## 5. Как записать демонстрацию

Запишите экран с открытым PowerShell. Покажите выполнение команд и их
реальные ответы, затем сохраните запись в GIF или формате asciinema,
как указано в ТЗ. Не нужно подставлять придуманные результаты.

В публичную запись не включайте реальные пароли и API-ключи.
Пароль `1234` здесь используется только для учебного пользователя.
