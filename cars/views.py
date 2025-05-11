import datetime
import logging
import os
import re

from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from xml.etree.ElementTree import parse

from .models import BodyType, Brand, Car, CarModel, Statistic
from .utils.data_processors import StatisticsProcessor
from .utils.response_utils import create_json_response


logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class AddCarsFromXML(View):
    def get(self, request):
        return Response(
            {"message": "Use POST method to add cars from XML"},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def post(self, request):
        logger.info("Starting XML import process")
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        xml_path = os.path.join(BASE_DIR, 'cars_project', 'data', 'Autocatalog.xml')

        try:
            tree = parse(xml_path)
            logger.info("XML file successfully parsed")
        except FileNotFoundError:
            logger.error("Autocatalog.xml file not found")
            return HttpResponse("Файл Autocatalog.xml не найден!", status=404)
        except Exception as e:
            logger.error(f"Error parsing XML file: {str(e)}")
            return HttpResponse(f"Ошибка обработки XML: {str(e)}", status=500)

        root = tree.getroot()
        success_count = 0
        error_count = 0

        for car in root.findall('car'):
            try:
                brand_name = car.find('brand').text.strip()
                model_name = car.find('model').text.strip()
                body_type = car.find('body_type').text.strip()

                clean_brand_name = re.sub(r'[^A-Za-zА-Яа-я\s]', '', brand_name)
                clean_model_name = re.sub(r'[^A-Za-zА-Яа-я\d\s]', '', model_name)

                self._save_car_data(clean_brand_name, clean_model_name, body_type)
                success_count += 1
            except Exception as e:
                logger.warning(f"Failed to process car entry: {str(e)}")
                error_count += 1

        logger.info(f"XML import completed. Success: {success_count}, Errors: {error_count}")
        return HttpResponse(
            f"Данные успешно добавлены. Успешно: {success_count}, Ошибок: {error_count}",
            status=200
        )

    def _save_car_data(self, brand_name, model_name, body_type):
        try:
            brand, created = Brand.objects.get_or_create(name=brand_name)
            if created:
                logger.debug(f"Created new brand: {brand_name}")

            car_model, created = CarModel.objects.get_or_create(
                brand=brand,
                name=model_name
            )
            if created:
                logger.debug(f"Created new model: {model_name}")

            body_type_obj, created = BodyType.objects.get_or_create(name=body_type)
            if created:
                logger.debug(f"Created new body type: {body_type}")

            car = Car.objects.create(model=car_model, body_type=body_type_obj)
            logger.debug(f"Created car: {brand_name} {model_name} {body_type}")

        except Exception as e:
            logger.error(f"Error saving car data: {str(e)}")
            raise


class StatisticsView(APIView):
    def get(self, request):
        logger.info("Processing statistics request")
        try:
            # Рассчитываем новую статистику при каждом запросе
            stats_data = StatisticsProcessor.calculate_car_statistics()
            StatisticsProcessor.save_statistics_to_db(stats_data)

            return create_json_response({
                'statistics': stats_data,
                'date_calculated': datetime.now().isoformat()
            })

        except Exception as e:
            logger.error(f"Error generating statistics: {str(e)}")
            # Пытаемся вернуть последние сохраненные данные, если есть
            try:
                latest_stat = Statistic.objects.latest('date_calculated')
                logger.warning("Returning cached statistics due to calculation error")
                return create_json_response({
                    'statistics': latest_stat.json_statistics,
                    'date_calculated': latest_stat.date_calculated,
                    'warning': 'Current statistics may be outdated'
                }, status=206)  # 206 Partial Content
            except Statistic.DoesNotExist:
                return create_json_response(
                    None,
                    status=503,
                    message=f"Statistics service unavailable: {str(e)}"
                )


class APIRootView(APIView):
    def get(self, request):
        endpoints = {
            'add-cars': request.build_absolute_uri('add/'),
            'statistics': request.build_absolute_uri('statistics/'),
            'swagger': request.build_absolute_uri('swagger/'),
            'redoc': request.build_absolute_uri('redoc/')
        }
        logger.debug(f"API root accessed. Available endpoints: {endpoints}")
        return Response(endpoints)