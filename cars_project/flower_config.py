import os

from celery import Celery
from django.conf import settings


app = Celery('cars_project')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Flower settings
FLOWER_BASIC_AUTH = [f"{os.getenv('FLOWER_USER')}:{os.getenv('FLOWER_PASSWORD')}"]
FLOWER_PORT = 5555
FLOWER_URL_PREFIX = 'flower'

