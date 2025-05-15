import logging
import os
import re
from xml.etree.ElementTree import parse

from django.db import close_old_connections, transaction
from rest_framework import status
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .models import BodyType, Brand, Car, CarModel, Statistic
from .utils.response_utils import create_json_response


logger = logging.getLogger(__name__)


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """Отключаем проверку CSRF для API """

    def enforce_csrf(self, request):
        return


class AddCarsFromXML(APIView):
    """
    API endpoint for adding cars from XML file
    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = [AllowAny]

    def post(self, request):
        """Handle POST request to import cars from XML"""
        close_old_connections()
        logger.info("Starting XML import process")

        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        xml_path = os.path.join(BASE_DIR, 'cars_project', 'data', 'Autocatalog.xml')

        try:
            tree = parse(xml_path)
            root = tree.getroot()
        except FileNotFoundError:
            logger.error("XML file not found")
            return create_json_response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Файл Autocatalog.xml не найден!"
            )

        cars_processed = 0
        errors = 0
        processed_brands = set()

        for modification in root.findall('.//Modification'):
            try:
                brand_name = modification.findtext('Make', '').strip()
                model_name = modification.findtext('Model', '').strip()
                body_type = modification.findtext('BodyType', '').strip()

                if not all([brand_name, model_name, body_type]):
                    continue

                clean_brand_name = re.sub(r'[^\w\s-]', '', brand_name, flags=re.UNICODE)
                clean_model_name = re.sub(r'[^\w\s-]', '', model_name, flags=re.UNICODE)
                clean_body_type = re.sub(r'[^\w\s-]', '', body_type, flags=re.UNICODE)

                if self.save_car_data(clean_brand_name, clean_model_name, clean_body_type):
                    cars_processed += 1
                    processed_brands.add(clean_brand_name)

            except Exception as e:
                errors += 1
                logger.error(f"Error processing modification: {str(e)}", exc_info=True)

        logger.info(f"Import completed. Processed: {cars_processed}, Errors: {errors}")
        return create_json_response(
            data={
                'cars_processed': cars_processed,
                'errors': errors,
                'brands_processed': len(processed_brands)
            },
            message=f"Успешно обработано {cars_processed} автомобилей"
        )

    @transaction.atomic
    def save_car_data(self, brand_name, model_name, body_type):
        try:
            # Проверка существования перед созданием
            if Car.objects.filter(
                    model__brand__name__iexact=brand_name,
                    model__name__iexact=model_name,
                    body_type__name__iexact=body_type
            ).exists():
                return False

            # Сначала пытаемся найти бренд без создания
            try:
                brand = Brand.objects.get(name__iexact=brand_name)
            except Brand.DoesNotExist:
                brand = Brand.objects.create(name=brand_name)
                # Дождемся сохранения бренда и получения его ID
                brand.refresh_from_db()

            # То же самое для модели автомобиля
            try:
                car_model = CarModel.objects.get(brand=brand, name__iexact=model_name)
            except CarModel.DoesNotExist:
                car_model = CarModel.objects.create(brand=brand, name=model_name)
                # Дождемся сохранения модели и получения ее ID
                car_model.refresh_from_db()

            # И для типа кузова
            try:
                body_type_obj = BodyType.objects.get(name__iexact=body_type)
            except BodyType.DoesNotExist:
                body_type_obj = BodyType.objects.create(name=body_type)
                # Дождемся сохранения типа кузова и получения его ID
                body_type_obj.refresh_from_db()

            car = Car.objects.create(model=car_model, body_type=body_type_obj)
            return True

        except Exception as e:
            logger.error(f"Error saving car: {str(e)}")
            # Перебрасываем исключение для обработки выше
            raise


class StatisticsView(APIView):
    """API endpoint for retrieving statistics"""

    def get(self, request):
        try:
            stats = {
                'total_brands': Brand.objects.count(),
                'total_models': CarModel.objects.count(),
                'total_cars': Car.objects.count(),
                'body_type_distribution': {
                    bt.name: Car.objects.filter(body_type=bt).count()
                    for bt in BodyType.objects.all()
                }
            }

            latest_stat = Statistic.objects.latest('date_calculated')
            return create_json_response({
                'statistics': latest_stat.json_statistics,
                'date_calculated': latest_stat.date_calculated,
                'current_stats': stats
            })

        except Statistic.DoesNotExist:
            return create_json_response(
                status=status.HTTP_404_NOT_FOUND,
                message="Статистика недоступна"
            )
        except Exception as e:
            logger.error(f"Error fetching statistics: {str(e)}")
            return create_json_response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Ошибка при получении статистики"
            )


class APIRootView(APIView):
    def get(self, request):
        endpoints = {
            'add-cars': request.build_absolute_uri('add/'),
            'statistics': request.build_absolute_uri('statistics/'),
            'swagger': request.build_absolute_uri('swagger/'),
            'redoc': request.build_absolute_uri('redoc/'),
            'flower': request.build_absolute_uri('flower/')
        }
        return create_json_response(data=endpoints)


class DuplicateFilter(logging.Filter):
    def filter(self, record):
        # Пропускаем дублирующиеся сообщения о существующих автомобилях
        if "Car exists" in record.msg:
            return False
        return True

logger.addFilter(DuplicateFilter())