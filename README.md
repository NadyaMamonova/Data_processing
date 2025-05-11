# Car Statistics API with Django, Celery and Redis

## Проект предоставляет API для обработки данных об автомобилях и автоматического сбора статистики с использованием Django, Celery и Redis.


🚀 Основные функции

    - Добавление данных из XML-файла в базу данных
    - Автоматический сбор статистики каждый час (Celery)
    - REST API для доступа к статистике
    - Интеграция с Redis как брокером сообщений
    - Система аудита изменений данных
    - Мониторинг задач через Flower
    - Документация API (Swagger/ReDoc)

🛠 Технологии

    - Python 3.9+
    - Django 4.2
    - Django REST Framework
    - Celery 5.3+
    - Redis 6.2+
    - PostgreSQL
    - Flower (мониторинг Celery)
    - Sentry (мониторинг ошибок)
    - drf-yasg (документация API)

⚙️ Установка
1. Клонирование репозитория

        git clone
        cd Data_processing
2. Настройка окружения

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

6. Настройка переменных окружения

Создайте файл .env на основе .env.template:

    cp .env.template .env

🔧 Конфигурация

Настройки в cars_project/settings.py


    DATABASES = {
     'default': {
         'ENGINE': 'django.db.backends.postgresql',
         'NAME': 'car_statistics',
         'USER': 'your_user',
         'PASSWORD': 'your_password',
         'HOST': 'localhost',
         'PORT': '5432',
     }
}


    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'

🚦 Запуск сервисов
1. Redis

       redis-server

2. Celery Worker

       celery -A cars_project worker --loglevel=info
        celery -A cars_project worker -l info -E

3. Celery Beat (для периодических задач)

       celery -A cars_project beat --loglevel=info

4. FLower(мониторинг):

       celery -A cars_project.flower_config flower --port=5555
       celery -A cars_project flower --port=5555

5. Django-сервер

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
    "metadata": {
        "timestamp": "2025-05-11T14:00:00Z",
        "status": 200,
        "message": "Success"
    },
    "data": {
        "total_brands": 15,
        "total_models": 42,
        "total_cars": 120,
        "body_type_distribution": {
            "Sedan": 50,
            "SUV": 40,
            "Hatchback": 30
        },
        "top_brands": [
            {
                "name": "Toyota",
                "model_count": 15,
                "car_count": 45
            }
        ]
    }
}

🔍 Администрирование

    Админ-панель: http://127.0.0.1:8000/admin/

    Flower (мониторинг): http://localhost:5555

    Swagger UI: http://127.0.0.1:8000/swagger/

    ReDoc: http://127.0.0.1:8000/redoc/