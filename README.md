# Req

- Poetry
- Python ^3.11
- PostgreSQL

# .env

```
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_DB=
POSTGRES_HOST=
```

# Запуск

```
poetry install
poetry shell
fastapi dev main.py
```

# Тест

```
poetry run pytest
```

# To Do

- async DB
- JWT auth
- alembic
- разделить регистрацию и авторизацию
- сделать логаут
- схемы ошибок в Swagger
- Auth in Swagger
- auth to middleware
- error enums
- разделить эндпоинты по файлам
- добавить поле owner_id в таблицу с доступом
