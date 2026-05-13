# Team Finder

Платформа для поиска участников в Pet-проекты по навыкам. Разработчики, дизайнеры и другие специалисты могут публиковать идеи проектов, формировать команду и откликаться на чужие проекты.

## Функциональность

- Регистрация и аутентификация по email и паролю
- Список проектов с фильтрацией по навыкам и постраничной пагинацией
- Создание, редактирование и завершение проектов
- Присоединение к проектам и добавление в избранное
- Профиль пользователя с навыками и историей проектов
- Управление навыками проекта и профиля через автодополнение (без перезагрузки страницы)
- Список всех пользователей с постраничной пагинацией

## Стек

- **Backend:** Python 3, Django 5.2, PostgreSQL
- **Frontend:** HTML/CSS, Vanilla JS
- **Инфраструктура:** Docker (только для PostgreSQL)
- **Зависимости:** psycopg2-binary, Pillow, python-decouple

## Развёртывание

### 1. Виртуальное окружение

```bash
python3 -m venv venv
```

- **Windows (PowerShell):** `venv\Scripts\Activate.ps1`
- **Windows (cmd):** `venv\Scripts\activate`
- **Linux/Mac:** `source venv/bin/activate`

```bash
pip install -r requirements.txt
```

### 2. Настройка окружения

```bash
cp .env_example .env
```

| Переменная            | Назначение                                     |
|-----------------------|------------------------------------------------|
| `DJANGO_SECRET_KEY`   | Секретный ключ Django                          |
| `DJANGO_DEBUG`        | Режим отладки (`True` для разработки)          |
| `POSTGRES_DB`         | Имя базы данных                                |
| `POSTGRES_USER`       | Пользователь PostgreSQL                        |
| `POSTGRES_PASSWORD`   | Пароль PostgreSQL                              |
| `POSTGRES_HOST`       | Хост БД (по умолчанию `localhost`)             |
| `POSTGRES_PORT`       | Порт БД (в `docker-compose.yml` — `5436`)      |
| `ALLOWED_HOSTS`       | Через запятую: `localhost,127.0.0.1`           |

### 3. База данных

```bash
docker compose up -d
```

PostgreSQL запускается на порте `5436`. Данные сохраняются в volume `postgres_data`.

```bash
docker compose down   # остановить
```

### 4. Миграции

```bash
python manage.py migrate
```

### 5. Тестовые данные

```bash
python manage.py create_test_data
```

Создаёт 3 пользователей с проектами:

| Email             | Пароль      |
|-------------------|-------------|
| alice@example.com | testpass123 |
| bob@example.com   | testpass123 |
| carol@example.com | testpass123 |

### 6. Запуск

```bash
python manage.py runserver
```

Сайт: [http://localhost:8000](http://localhost:8000)  
Админка: [http://localhost:8000/admin/](http://localhost:8000/admin/)

Для создания суперпользователя: `python manage.py createsuperuser`

## Автор

Vitaliy Polikanов
