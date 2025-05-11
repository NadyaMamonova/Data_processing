# cars/utils/data_processors.py
import logging
from django.db import models
from ..models import Brand, CarModel, BodyType, Car, Statistic
from datetime import datetime

logger = logging.getLogger(__name__)


class StatisticsProcessor:
    @staticmethod
    def calculate_car_statistics():
        """
        Рассчитывает статистику по автомобилям с логгированием каждого этапа
        """
        statistics = {}

        try:
            # Статистика по типам кузова
            logger.info("Starting body type statistics calculation")
            body_type_stats = StatisticsProcessor._calculate_body_type_stats()
            statistics['body_types'] = body_type_stats
            logger.info("Body type statistics calculated successfully")
        except Exception as e:
            logger.error(f"Error calculating body type stats: {str(e)}")
            statistics['body_types'] = {'error': str(e)}

        try:
            # Топ 5 брендов по количеству моделей
            logger.info("Starting top brands statistics calculation")
            top_brands = StatisticsProcessor._calculate_top_brands()
            statistics['top_brands'] = top_brands
            logger.info("Top brands statistics calculated successfully")
        except Exception as e:
            logger.error(f"Error calculating top brands stats: {str(e)}")
            statistics['top_brands'] = {'error': str(e)}

        try:
            # Общая статистика
            logger.info("Starting general statistics calculation")
            general_stats = StatisticsProcessor._calculate_general_stats()
            statistics['general'] = general_stats
            logger.info("General statistics calculated successfully")
        except Exception as e:
            logger.error(f"Error calculating general stats: {str(e)}")
            statistics['general'] = {'error': str(e)}

        return statistics

    @staticmethod
    def _calculate_body_type_stats():
        """Рассчитывает статистику по типам кузова"""
        try:
            body_types = BodyType.objects.all().prefetch_related('car_set')
            stats = {
                bt.name: bt.car_set.count()
                for bt in body_types
            }
            return stats
        except Exception as e:
            logger.error(f"Error in _calculate_body_type_stats: {str(e)}")
            raise

    @staticmethod
    def _calculate_top_brands():
        """Рассчитывает топ 5 брендов по количеству автомобилей"""
        try:
            top_brands = Brand.objects.annotate(
                car_count=models.Count('carmodel__car')
            ).order_by('-car_count')[:5]

            return [
                {
                    'brand': brand.name,
                    'car_count': brand.car_count
                }
                for brand in top_brands
            ]
        except Exception as e:
            logger.error(f"Error in _calculate_top_brands: {str(e)}")
            raise

    @staticmethod
    def _calculate_general_stats():
        """Рассчитывает общую статистику"""
        try:
            return {
                'total_brands': Brand.objects.count(),
                'total_models': CarModel.objects.count(),
                'total_cars': Car.objects.count(),
                'calculation_time': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in _calculate_general_stats: {str(e)}")
            raise

    @staticmethod
    def save_statistics_to_db(statistics_data):
        """
        Сохраняет статистику в базу данных с логгированием
        """
        try:
            logger.info("Starting to save statistics to database")

            stats = Statistic.objects.create(
                json_statistics=statistics_data
            )

            logger.info(f"Statistics successfully saved to DB with ID {stats.id}")
            return stats

        except Exception as e:
            logger.error(f"Error saving statistics to DB: {str(e)}")
            raise