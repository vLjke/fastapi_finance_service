# FastAPI Finance Service

Учебный сервис на FastAPI для учета финансовых операций:

- регистрация и аутентификация пользователя;
- создание и просмотр кошельков;
- добавление доходов и расходов;
- получение истории транзакций.

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn app.main:app --reload
```

После запуска API будет доступно по адресу:

- `http://127.0.0.1:8000`
- документация: `http://127.0.0.1:8000/docs`
# Personal Finance & Budget Service
