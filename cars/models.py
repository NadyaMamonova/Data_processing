from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Brand(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name = "Brand"
        verbose_name_plural = "Brands"

    def __str__(self):
        return self.name


class CarModel(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = ('brand', 'name')  # Уникальная пара бренд+модель


class BodyType(models.Model):
    name = models.CharField(max_length=50, unique=True)


class Configuration(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Car(models.Model):
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE)
    body_type = models.ForeignKey(BodyType, on_delete=models.SET_NULL, null=True)
    configurations = models.ManyToManyField(Configuration)

    class Meta:
        unique_together = ('model', 'body_type')  # Уникальная комбинация

class Statistic(models.Model):
    json_statistics = models.JSONField()  # Поле для хранения статистики в формате JSON
    date_calculated = models.DateTimeField(auto_now_add=True)  # Дата расчета статистики

    class Meta:
        verbose_name_plural = "Statistics"  # Название модели

    def __str__(self):
        return f"Статистика от {self.date_calculated}"

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('C', 'Created'),
        ('U', 'Updated'),
        ('D', 'Deleted')
    ]

    model_name = models.CharField(max_length=50)
    object_id = models.PositiveIntegerField(null=True)  # Разрешим null для object_id
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    changes = models.JSONField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']


class Model:
    pass


class Modification:
    pass