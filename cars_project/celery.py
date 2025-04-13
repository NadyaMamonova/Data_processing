from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cars_project.settings')

app = Celery('cars_project')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Настройка периодических задач
app.conf.beat_schedule = {
    'collect-stats-every-hour': {
        'task': 'cars_project.tasks.collect_and_save_stats',
        'schedule': crontab(minute=0),  # каждый час в 0 минут
    },
}

app.autodiscover_tasks()