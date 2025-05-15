import os

from django.conf import settings
from celery import Celery

from cars_project.celery import app


app = Celery('cars_project')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Flower settings
FLOWER_BASIC_AUTH = [f"{os.getenv('FLOWER_USER')}:{os.getenv('FLOWER_PASSWORD')}"]
FLOWER_PORT = 5555
FLOWER_URL_PREFIX = 'flower'
