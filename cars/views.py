import logging
import os
import re
from xml.etree.ElementTree import parse
from xml.etree import ElementTree as ET

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
    API endpoint for adding cars from XML file or JSON data
    """
    authentication_classes = (CsrfExemptSessionAuthentication, BasicAuthentication)
    permission_classes = [AllowAny]

    # Константы для путей и настроек
    XML_RELATIVE_PATH = os.path.join('cars_project', 'data', 'Autocatalog.xml')
    CLEAN_PATTERN = re.compile(r'[^\w\s-]', flags=re.UNICODE)

    def post(self, request):
        """Handle POST request to import cars from XML or JSON"""
        close_old_connections()
        logger.info(f"Received request with data: {request.data}")

        try:
            if request.content_type == 'application/json':
                return self.handle_json_import(request.data)
            return self.handle_xml_import()
        except Exception as e:
            logger.error(f"Unexpected error in post handler: {str(e)}", exc_info=True)
            return create_json_response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Внутренняя ошибка сервера"
            )

    def handle_xml_import(self):
        """Process XML file import"""
        logger.info("Starting XML import process")

        try:
            # Получаем абсолютный путь к XML файлу
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            xml_path = os.path.abspath(os.path.join(base_dir, self.XML_RELATIVE_PATH))

            # Проверяем существование файла перед парсингом
            if not os.path.exists(xml_path):
                logger.error(f"XML file not found at: {xml_path}")
                return create_json_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="XML файл не найден",
                    data={"expected_path": xml_path}
                )

            # Парсинг XML
            tree = parse(xml_path)
            root = tree.getroot()

            results = {
                'cars_processed': 0,
                'errors': 0,
                'processed_brands': set(),
                'skipped': 0,
                'invalid_entries': 0
            }

            # Обработка модификаций
            for modification in root.findall('.//Modification'):
                try:
                    brand = modification.findtext('Make', '').strip()
                    model = modification.findtext('Model', '').strip()
                    body = modification.findtext('BodyType', '').strip()

                    # Пропускаем записи с пустыми полями
                    if not all((brand, model, body)):
                        results['invalid_entries'] += 1
                        continue

                    # Очистка данных
                    clean_data = {
                        'brand': self._clean_string(brand),
                        'model': self._clean_string(model),
                        'body_type': self._clean_string(body)
                    }

                    # Сохранение в БД
                    if self.save_car_data(**clean_data):
                        results['cars_processed'] += 1
                        results['processed_brands'].add(clean_data['brand'])
                    else:
                        results['skipped'] += 1

                except Exception as e:
                    results['errors'] += 1
                    logger.error(f"Error processing modification: {str(e)}", exc_info=True)

            logger.info(f"XML import completed. Stats: {results}")
            return create_json_response(
                status=status.HTTP_200_OK,
                data=results,
                message=f"Обработано {results['cars_processed']} автомобилей"
            )

        except ET.ParseError as e:
            logger.error(f"XML parsing error: {str(e)}")
            return create_json_response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Ошибка разбора XML файла"
            )
        except Exception as e:
            logger.error(f"Unexpected error in XML import: {str(e)}", exc_info=True)
            return create_json_response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Внутренняя ошибка при обработке XML"
            )

    def handle_json_import(self, data):
        """Process JSON data import"""
        logger.info("Processing JSON data import")

        required_fields = {'brand', 'model', 'body_type'}
        missing_fields = required_fields - set(data.keys())

        if missing_fields:
            return create_json_response(
                status=status.HTTP_400_BAD_REQUEST,
                message=f"Отсутствуют обязательные поля: {', '.join(missing_fields)}"
            )

        try:
            clean_data = {
                'brand': self._clean_string(data['brand']),
                'model': self._clean_string(data['model']),
                'body_type': self._clean_string(data['body_type'])
            }

            if not all(clean_data.values()):
                return create_json_response(
                    status=status.HTTP_400_BAD_REQUEST,
                    message="Все поля должны содержать непустые значения"
                )

            if self.save_car_data(**clean_data):
                return create_json_response(
                    status=status.HTTP_201_CREATED,
                    message=f"Автомобиль {clean_data['brand']} {clean_data['model']} успешно добавлен",
                    data=clean_data
                )
            return create_json_response(
                status=status.HTTP_200_OK,
                message="Автомобиль уже существует в базе",
                data=clean_data
            )

        except Exception as e:
            logger.error(f"JSON processing error: {str(e)}", exc_info=True)
            return create_json_response(
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                message="Ошибка при обработке данных"
            )

    def _clean_string(self, value):
        """Clean and normalize string data"""
        return self.CLEAN_PATTERN.sub('', value.strip()) if value else ''

    @transaction.atomic
    def save_car_data(self, brand, model, body_type):
        """Save car data to database (atomic transaction)"""
        try:
            if Car.objects.filter(
                    model__brand__name__iexact=brand,
                    model__name__iexact=model,
                    body_type__name__iexact=body_type
            ).exists():
                logger.debug(f"Car exists: {brand} {model} {body_type}")
                return False

            brand_obj = Brand.objects.get_or_create(
                name__iexact=brand,
                defaults={'name': brand}
            )[0]

            model_obj = CarModel.objects.get_or_create(
                brand=brand_obj,
                name__iexact=model,
                defaults={'name': model}
            )[0]

            body_type_obj = BodyType.objects.get_or_create(
                name__iexact=body_type,
                defaults={'name': body_type}
            )[0]

            Car.objects.create(model=model_obj, body_type=body_type_obj)
            logger.info(f"Created car: {brand} {model} {body_type}")
            return True

        except Exception as e:
            logger.error(f"DB save error: {str(e)}", exc_info=True)
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