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
       celery -A cars_project worker --loglevel=info -I cars_project.tasks


3. Celery Beat (для периодических задач)

       celery -A cars_project beat --loglevel=info

4. FLower(мониторинг):

       celery -A cars_project.flower_config flower --port=5555
       celery -A cars_project flower --port=5555

5. Django-сервер

       python manage.py runserver

📡 API Endpoints

1. Проверить корневой эндпоинт API:

curl http://127.0.0.1:8000/api/

2. Проверить корневой URL:   

curl http://127.0.0.1:8000/

3. Проверить доступ к приложению cars:

curl http://127.0.0.1:8000/cars/

4. Получение статистики
    
    curl http://127.0.0.1:8000/api/statistics/


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


# Скрипт для запуска Django, Redis и Celery

Этот bash-скрипт автоматизирует запуск:

    Redis (если не запущен)

    Celery Worker (асинхронные задачи)

    Celery Beat (периодические задачи)

    Flower (мониторинг Celery)

    Django development server

Как использовать?

    Убедитесь, что установлены:

        Redis (sudo apt install redis / brew install redis)

        Celery (pip install celery)

        Flower (pip install flower)

Дайте скрипту права на выполнение:

    bash
    chmod +x run_dev.sh

Запустите скрипт:

    bash
    ./run_dev.sh

Что делает скрипт?

    Проверяет, запущен ли Redis

    Если нет → запускает redis-server в фоне.

    Останавливает старые процессы Celery (если есть)

        celery worker

        celery beat

        flower

    Запускает компоненты Celery

        Worker (celery -A cars_project worker)

        Beat (celery -A cars_project beat)

        Flower (мониторинг на http://localhost:5555)

    Запускает Django-сервер (python manage.py runserver)

Порт по умолчанию:

    Redis → 6379

    Django → 8000

    Flower → 5555

Если порты заняты → измените их в скрипте.
Пример вывода при запуске

    bash
    Starting Redis server...
    Starting Celery worker...
    Starting Celery Beat...
    Starting Flower...
    Starting Django server...

Как остановить все процессы?
bash

    pkill -f "celery -A cars_project"
    pkill -f "redis-server"