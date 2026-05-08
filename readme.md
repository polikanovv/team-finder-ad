# Team Finder

Платформа для поиска участников в проекты по навыкам.

---

## Инструкция для ревьюера

### 1. Виртуальное окружение

Создайте и активируйте виртуальное окружение Python:

```bash
python3 -m venv venv
```

- **Windows (PowerShell):** `venv\Scripts\Activate.ps1`
- **Windows (cmd):** `venv\Scripts\activate`
- **Linux/Mac:** `source venv/bin/activate`

Установите зависимости:

```bash
pip install -r requirements.txt
```

### 2. Создание `.env`

Скопируйте пример:

```bash
cp .env_example .env
```

Заполните `.env`. Для варианта 3 установите `TASK_VERSION=3`.

| Переменная            | Назначение                                                        |
|-----------------------|-------------------------------------------------------------------|
| **DJANGO_SECRET_KEY** | Секретный ключ Django                                             |
| **DJANGO_DEBUG**      | Режим отладки (`True` для разработки)                             |
| **POSTGRES_DB**       | Имя базы данных                                                   |
| **POSTGRES_USER**     | Пользователь PostgreSQL                                           |
| **POSTGRES_PASSWORD** | Пароль PostgreSQL                                                 |
| **POSTGRES_HOST**     | Хост БД (`localhost` для локальной разработки)                    |
| **POSTGRES_PORT**     | Порт БД (в `docker-compose.yml` прописан `5436`)                  |
| **TASK_VERSION**      | Номер варианта задания (определяет набор шаблонов: 1, 2 или 3)    |

### 3. Запуск базы данных

База данных запускается в Docker-контейнере:

```bash
docker compose up -d
```

PostgreSQL будет доступен на порте `5436` (настраивается в `.env` и `docker-compose.yml`).

Остановить:

```bash
docker compose down
```

Данные сохраняются в Docker volume `postgres_data` и не теряются при перезапуске.

### 4. Применение миграций

```bash
python manage.py migrate
```

### 5. Загрузка тестовых данных

В проекте есть команда для создания тестовых пользователей и проектов:

```bash
python manage.py create_test_data
```

Будут созданы 3 пользователя (у каждого минимум 1 проект):

| Email                | Пароль      |
|----------------------|-------------|
| alice@example.com    | testpass123 |
| bob@example.com      | testpass123 |
| carol@example.com    | testpass123 |

### 6. Запуск сервера

```bash
python manage.py runserver
```

Сайт доступен по адресу: [http://localhost:8000](http://localhost:8000)

### 7. Администратор (опционально)

Для создания суперпользователя:

```bash
python manage.py createsuperuser
```

Панель администратора: [http://localhost:8000/admin/](http://localhost:8000/admin/)
