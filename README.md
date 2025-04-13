# Car Statistics API with Django, Celery, and Redis

## Проект предоставляет API для обработки данных об автомобилях и автоматического сбора статистики с использованием Django, Celery и Redis.
🚀 Основные функции

    Добавление данных из XML-файла в базу данных

    Автоматический сбор статистики каждый час (Celery)

    REST API для доступа к статистике

    Интеграция с Redis как брокером сообщений

🛠 Технологии

    Python 3.9+

    Django 4.2

    Django REST Framework

    Celery 5.3+

    Redis 6.2+

    SQLite (для разработки)

⚙️ Установка
1. Клонирование репозитория
bash
Copy

        git clone
        cd Data_processing

2.Настройка окружения

    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows

3. Установка зависимостей

        pip install -r requirements.txt

4. Настройка базы данных

       python manage.py makemigrations
       python manage.py migrate

5. Создание суперпользователя (опционально)

       python manage.py createsuperuser

🔧 Конфигурация

Настройки в cars_project/settings.py


    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'

🚦 Запуск сервисов
1. Redis

       redis-server

2. Celery Worker

       celery -A cars_project worker --loglevel=info

3. Celery Beat (для периодических задач)

       celery -A cars_project beat --loglevel=info

4. Django-сервер

       python manage.py runserver

📡 API Endpoints
1. Добавление данных из XML


    POST /cars/add/

Пример:

    curl -X POST http://127.0.0.1:8000/cars/add/

2. Получение статистики

        GET /cars/statistics/

Пример ответа:
json

{
    "data": {
        "total_brands": 15,
        "total_cars": 42
    },
    "date_calculated": "2025-04-13T12:00:00Z"
}

🔍 Администрирование

Доступ к админке:
http://127.0.0.1:8000/admin/
