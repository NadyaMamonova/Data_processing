import json
import time

from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from django.utils import timezone

from cars import models
from cars.models import (BodyType, Brand, Car, CarModel, Statistic)


logger = get_task_logger(__name__)

@shared_task(bind=True)
def collect_and_save_stats(self):
    """Сбор и сохранение статистики с подробным логированием"""
    stats = {}
    start_time = time.time()

    try:
        # 1. Общая статистика
        try:
            stats['total_brands'] = Brand.objects.count()
            stats['total_models'] = CarModel.objects.count()
            stats['total_cars'] = Car.objects.count()
            logger.info("Basic counts calculated successfully")
        except Exception as e:
            logger.error(f"Error calculating basic counts: {str(e)}")
            raise

        # 2. Распределение по типам кузова
        body_stats = {}
        try:
            for bt in BodyType.objects.all():
                try:
                    count = Car.objects.filter(body_type=bt).count()
                    body_stats[bt.name] = count
                    logger.debug(f"Body type {bt.name} count: {count}")
                except Exception as e:
                    logger.error(f"Error counting body type {bt.name}: {str(e)}")
                    body_stats[bt.name] = 'error'
            stats['body_type_distribution'] = body_stats
        except Exception as e:
            logger.error(f"Error calculating body type stats: {str(e)}")
            stats['body_type_distribution'] = 'error'

        # 3. Топ брендов
        try:
            top_brands = []
            for brand in Brand.objects.annotate(
                    car_count=models.Count('carmodel__car')
            ).order_by('-car_count')[:5]:
                try:
                    brand_data = {
                        'name': brand.name,
                        'model_count': brand.carmodel_set.count(),
                        'car_count': brand.car_count
                    }
                    top_brands.append(brand_data)
                    logger.debug(f"Processed brand {brand.name}")
                except Exception as e:
                    logger.error(f"Error processing brand {brand.name}: {str(e)}")
            stats['top_brands'] = top_brands
        except Exception as e:
            logger.error(f"Error calculating top brands: {str(e)}")
            stats['top_brands'] = 'error'

        # 4. Сохранение статистики
        try:
            with transaction.atomic():
                stat_record = Statistic.objects.create(
                    json_statistics=stats,
                    date_calculated=timezone.now()
                )
                logger.info(f"Statistics saved with ID {stat_record.id}")

            execution_time = time.time() - start_time
            logger.info(f"Statistics collection completed in {execution_time:.2f} seconds")

            return {
                'status': 'success',
                'execution_time': execution_time,
                'statistics_id': stat_record.id
            }

        except Exception as e:
            logger.error(f"Error saving statistics: {str(e)}")
            raise

    except Exception as e:
        logger.critical(f"Statistics collection failed: {str(e)}")
        return {
            'status': 'error',
            'error': str(e)
        }