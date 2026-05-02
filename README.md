# Personal Finance & Budget Service

Учебный сервис на FastAPI для учета личных финансов:

- регистрация и аутентификация пользователя;
- создание и просмотр кошельков;
- добавление доходов и расходов;
- получение истории транзакций.

## Установка

```bash
python -m venv .venv
```

Активируйте виртуальное окружение:

- Windows PowerShell:
```bash
.\.venv\Scripts\Activate.ps1
```
- Windows CMD:
```bash
.venv\Scripts\activate.bat
```
- macOS/Linux:
```bash
source .venv/bin/activate
```

Установите зависимости:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Запуск сервиса

```bash
python -m uvicorn app.main:app --reload
```

После запуска API будет доступно по адресу:

- `http://127.0.0.1:8000`
- документация: `http://127.0.0.1:8000/docs`

## Запуск тестов

```bash
python -m pytest -q
```
