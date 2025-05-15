import logging
from datetime import datetime

from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from cars.models import AuditLog, BodyType, Brand, Model, Modification


logger = logging.getLogger(__name__)

@receiver(post_save, sender=Brand)
@receiver(post_save, sender=Model)
@receiver(post_save, sender=BodyType)
@receiver(post_save, sender=Modification)
def log_model_save(sender, instance, created, **kwargs):
    """
    Обрабатывает сигнал сохранения модели и создает запись в журнале аудита

    Args:
        sender: Класс модели, которая вызвала сигнал
        instance: Экземпляр сохраненной модели
        created: Флаг, указывающий, был ли создан новый объект
    """
    try:
        action = 'create' if created else 'update'
        model_name = sender.__name__

        # Сериализуем объект для журнала
        instance_data = {
            'id': instance.id,
            'model': model_name,
        }

        # Добавляем атрибуты модели в данные
        for field in instance._meta.fields:
            field_name = field.name
            if field_name != 'id' and hasattr(instance, field_name):
                value = getattr(instance, field_name)
                # Обработка связей внешних ключей
                if field.is_relation and value is not None:
                    instance_data[field_name] = value.id
                else:
                    instance_data[field_name] = str(value) if value is not None else None

        # Создаем запись в журнале аудита
        AuditLog.objects.create(
            action=f'{model_name}_{action}',
            changes=instance_data,
            timestamp=datetime.now()
        )

        logger.info(f"Audit log created for {model_name} {action}")

    except Exception as e:
        logger.error(f"Failed to create audit log for {sender.__name__}: {str(e)}")


@receiver(post_delete, sender=Brand)
@receiver(post_delete, sender=Model)
@receiver(post_delete, sender=BodyType)
@receiver(post_delete, sender=Modification)
def log_model_delete(sender, instance, **kwargs):
    """
    Обрабатывает сигнал удаления модели и создает запись в журнале аудита

    Args:
        sender: Класс модели, которая вызвала сигнал
        instance: Экземпляр удаленной модели
    """
    try:
        model_name = sender.__name__

        # Сериализуем удаленный объект для журнала
        instance_data = {
            'id': instance.id,
            'model': model_name,
        }

        # Добавляем основные атрибуты модели в данные
        for field in instance._meta.fields:
            field_name = field.name
            if field_name != 'id' and hasattr(instance, field_name):
                value = getattr(instance, field_name)
                # Обработка связей
                if field.is_relation and value is not None:
                    instance_data[field_name] = value.id
                else:
                    instance_data[field_name] = str(value) if value is not None else None

        # Создаем запись в журнале аудита
        AuditLog.objects.create(
            action=f'{model_name}_delete',
            changes=instance_data,
            timestamp=datetime.now()
        )

        logger.info(f"Audit log created for {model_name} delete")

    except Exception as e:
        logger.error(f"Failed to create audit log for {sender.__name__} deletion: {str(e)}")


@receiver(post_save, sender=User)
def log_user_action(sender, instance, created, **kwargs):
    """
    Отслеживает действия пользователей

    Args:
        sender: Класс модели User
        instance: Экземпляр пользователя
        created: Флаг создания нового пользователя
    """
    try:
        action = 'create' if created else 'update'

        # Сериализуем только нужные поля пользователя
        user_data = {
            'id': instance.id,
            'username': instance.username,
            'is_active': instance.is_active,
            'is_staff': instance.is_staff,
            'is_superuser': instance.is_superuser,
            'last_login': str(instance.last_login) if instance.last_login else None,
            'date_joined': str(instance.date_joined) if instance.date_joined else None
        }

        # Создаем запись в журнале аудита
        AuditLog.objects.create(
            action=f'user_{action}',
            changes=user_data,
            timestamp=datetime.now()
        )

        logger.info(f"Audit log created for User {action}")

    except Exception as e:
        logger.error(f"Failed to create audit log for User: {str(e)}")