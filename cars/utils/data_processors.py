import logging
import xml.etree.ElementTree as ET
from datetime import datetime

from django.db import models, transaction
from django.db.models import Avg, Count

from cars.models import AuditLog, BodyType, Brand, Modification, Model


logger = logging.getLogger(__name__)

class CarDataProcessor:
    """
    Класс для обработки данных об автомобилях
    """

    def __init__(self, xml_path=None):
        self.xml_path = xml_path

    def process_xml_data(self, xml_path=None):
        """
        Обрабатывает XML файл и сохраняет данные в базу данных

        Args:
            xml_path: Путь к XML файлу с данными об автомобилях

        Returns:
            dict: Статистика импорта данных
        """
        try:
            path = xml_path or self.xml_path
            if not path:
                raise ValueError("XML path is not specified")

            logger.info(f"Starting XML processing from {path}")

            # Парсинг XML
            tree = ET.parse(path)
            root = tree.getroot()

            stats = {
                'brands_created': 0,
                'models_created': 0,
                'modifications_created': 0,
                'body_types_created': 0,
                'errors': 0
            }

            # Обработка данных в транзакции
            with transaction.atomic():
                # Обработка брендов
                for brand_elem in root.findall('./brands/brand'):
                    try:
                        brand_name = brand_elem.get('name')
                        brand, created = Brand.objects.get_or_create(name=brand_name)

                        if created:
                            stats['brands_created'] += 1
                            logger.debug(f"Created brand: {brand_name}")

                        # Обработка моделей
                        for model_elem in brand_elem.findall('./models/model'):
                            model_name = model_elem.get('name')
                            model, model_created = Model.objects.get_or_create(
                                brand=brand,
                                name=model_name
                            )

                            if model_created:
                                stats['models_created'] += 1

                            # Обработка типов кузова
                            for body_elem in model_elem.findall('./body_types/body_type'):
                                body_name = body_elem.get('name')
                                body_type, body_created = BodyType.objects.get_or_create(name=body_name)

                                if body_created:
                                    stats['body_types_created'] += 1

                                # Обработка модификаций
                                for mod_elem in body_elem.findall('./modifications/modification'):
                                    mod_name = mod_elem.get('name')
                                    engine = mod_elem.get('engine', '')
                                    power = int(mod_elem.get('power', 0))
                                    fuel_type = mod_elem.get('fuel', '')

                                    mod, mod_created = Modification.objects.get_or_create(
                                        model=model,
                                        body_type=body_type,
                                        name=mod_name,
                                        defaults={
                                            'engine': engine,
                                            'power': power,
                                            'fuel_type': fuel_type
                                        }
                                    )

                                    if mod_created:
                                        stats['modifications_created'] += 1

                    except Exception as e:
                        stats['errors'] += 1
                        logger.error(f"Error processing brand: {str(e)}")

            # Запись в аудит
            AuditLog.objects.create(
                action='import_xml',
                data=stats,
                timestamp=datetime.now()
            )

            logger.info(f"XML processing completed. Stats: {stats}")
            return stats

        except Exception as e:
            logger.error(f"Failed to process XML: {str(e)}")
            # Запись в аудит об ошибке
            AuditLog.objects.create(
                action='import_xml_error',
                data={'error': str(e)},
                timestamp=datetime.now()
            )
            raise

    def get_car_statistics(self):
        """
        Собирает и возвращает статистику по автомобилям

        Returns:
            dict: Статистика по автомобилям
        """
        try:
            logger.info("Generating car statistics")

            # Базовая статистика
            stats = {
                'total_brands': Brand.objects.count(),
                'total_models': Model.objects.count(),
                'total_modifications': Modification.objects.count(),
                'total_body_types': BodyType.objects.count(),
                'average_power': Modification.objects.aggregate(avg_power=Avg('power'))['avg_power'],
                'top_brands': self._calculate_top_brands(),
                'fuel_type_distribution': self._get_fuel_distribution(),
                'body_type_distribution': self._get_body_type_distribution()
            }

            logger.info("Statistics generated successfully")
            return stats

        except Exception as e:
            logger.error(f"Failed to generate statistics: {str(e)}")
            raise

    def _calculate_top_brands(self, limit=5):
        """
        Рассчитывает топ-N брендов по количеству моделей

        Args:
            limit: Количество брендов в топе

        Returns:
            list: Список брендов и количество моделей
        """
        top_brands = Brand.objects.annotate(
            models_count=Count('model')
        ).order_by('-models_count')[:limit]

        return [
            {
                'brand': brand.name,
                'models_count': brand.models_count,
                'average_power': Modification.objects.filter(
                    model__brand=brand
                ).aggregate(avg=Avg('power'))['avg'] or 0
            }
            for brand in top_brands
        ]

    def _get_fuel_distribution(self):
        """
        Рассчитывает распределение по типам топлива

        Returns:
            dict: Распределение по типам топлива
        """
        fuel_types = Modification.objects.values('fuel_type').annotate(
            count=Count('id')
        ).order_by('-count')

        return {item['fuel_type'] or 'Unknown': item['count'] for item in fuel_types}

    def _get_body_type_distribution(self):
        """
        Рассчитывает распределение по типам кузова

        Returns:
            dict: Распределение по типам кузова
        """
        body_types = Modification.objects.values('body_type__name').annotate(
            count=Count('id')
        ).order_by('-count')

        return {item['body_type__name'] or 'Unknown': item['count'] for item in body_types}