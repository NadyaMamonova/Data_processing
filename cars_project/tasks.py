# from celery import shared_task
# from django.utils import timezone
#
# from Data_processing.cars_project.cars.models import Statistic
#
#
# @shared_task
# def collect_and_save_stats():
#     # Логика сбора статистики
#     statistic_data = {"some_key": "some_value"}  # Пример данных статистики
#
#     # Сохранение собранной статистики в базу данных
#     Statistic.objects.create(json_statistics=statistic_data, date_calculated=timezone.now())

from celery import shared_task
from cars.models import Brand, CarModel, BodyType, Car, Statistic
from django.utils import timezone
import json


@shared_task
def collect_and_save_stats():
    # Собираем статистику
    stats = {
        'total_brands': Brand.objects.count(),
        'total_models': CarModel.objects.count(),
        'total_cars': Car.objects.count(),
        'body_type_distribution': {
            bt.name: Car.objects.filter(body_type=bt).count()
            for bt in BodyType.objects.all()
        },
        'top_brands': [
            {
                'name': brand.name,
                'model_count': brand.carmodel_set.count(),
                'car_count': Car.objects.filter(model__brand=brand).count()
            }
            for brand in Brand.objects.annotate(
                car_count=models.Count('carmodel__car')
            ).order_by('-car_count')[:5]
        ]
    }

    # Сохраняем в базу
    Statistic.objects.create(
        json_statistics=json.dumps(stats),
        date_calculated=timezone.now()
    )

    return "Статистика успешно собрана и сохранена"