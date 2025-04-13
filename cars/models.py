from django.db import models


class Brand(models.Model):
    name = models.CharField(max_length=100)

class CarModel(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

class BodyType(models.Model):
    name = models.CharField(max_length=50)

class Configuration(models.Model):
    name = models.CharField(max_length=100)

class Car(models.Model):
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    body_type = models.ForeignKey(BodyType, on_delete=models.SET_NULL, null=True)
    configurations = models.ManyToManyField(Configuration)


class Statistic(models.Model):
    json_statistics = models.JSONField()  # Поле для хранения статистики в формате JSON
    date_calculated = models.DateTimeField(auto_now_add=True)  # Дата расчета статистики

    class Meta:
        verbose_name_plural = "Statistics"  # Название модели

    def __str__(self):
        return f"Статистика от {self.date_calculated}"


