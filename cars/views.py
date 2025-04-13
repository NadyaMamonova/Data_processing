from django.views import View
from xml.etree.ElementTree import parse
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.views import APIView
from .models import Brand, CarModel, BodyType, Car, Statistic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import re
import os


@method_decorator(csrf_exempt, name='dispatch')
class AddCarsFromXML(View):
    def post(self, request):
        # Определяем путь к XML-файлу
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        xml_path = os.path.join(BASE_DIR, 'cars_project', 'data', 'Autocatalog.xml')

        try:
            tree = parse(xml_path)
        except FileNotFoundError:
            return HttpResponse("Файл Autocatalog.xml не найден!")

        root = tree.getroot()
        for car in root.findall('car'):
            # Извлечение данных
            brand_name = car.find('brand').text.strip()
            model_name = car.find('model').text.strip()
            body_type = car.find('body_type').text.strip()

            # Очистка данных с помощью регулярных выражений
            clean_brand_name = re.sub(r'[^A-Za-zА-Яа-я\s]', '', brand_name)
            clean_model_name = re.sub(r'[^A-Za-zА-Яа-я\d\s]', '', model_name)

            # Сохранение данных
            save_car_data(clean_brand_name, clean_model_name, body_type)

        return HttpResponse("Данные успешно добавлены")


# Функция для сохранения данных
def save_car_data(brand_name, model_name, body_type):
    # Применяем регулярное выражение для очистки данных
    clean_brand_name = re.sub(r'[^A-Za-zА-Яа-я\s]', '', brand_name)
    clean_model_name = re.sub(r'[^A-Za-zА-Яа-я\d\s]', '', model_name)

    try:
        # Проверяем наличие бренда и создаем новый, если его нет
        brand, _ = Brand.objects.get_or_create(name=clean_brand_name)

        # Аналогично проверяем модель автомобиля
        car_model, _ = CarModel.objects.get_or_create(
            brand=brand,
            name=clean_model_name
        )

        # Сохраняем тип кузова
        body_type_obj, _ = BodyType.objects.get_or_create(name=body_type)

        # Создаем запись автомобиля
        car = Car.objects.create(model=car_model, body_type=body_type_obj)

        print(f"Сохранено: {brand.name}, {car_model.name}, {body_type}")

    except Exception as e:
        print(f"Произошла ошибка при сохранении данных: {e}")


class StatisticsView(APIView):
    def get(self, request):
        try:
            latest_stat = Statistic.objects.latest('date_calculated')
            return Response({
                'data': latest_stat.json_statistics,
                'date_calculated': latest_stat.date_calculated
            })
        except Statistic.DoesNotExist:
            return Response(
                {"error": "No statistics available"},
                status=404
            )