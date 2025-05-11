import logging

from django.contrib.auth import get_user_model
from django.db import transaction, connections
from django.db.models.signals import pre_delete, pre_save, post_save
from django.dispatch import receiver

from ..models import AuditLog


logger = logging.getLogger(__name__)
User = get_user_model()


def get_current_user():
    """Получение текущего пользователя из запроса"""
    from django.core.handlers.wsgi import WSGIRequest
    from django.db import DEFAULT_DB_ALIAS

    try:
        request = None
        for conn in connections.all():
            if hasattr(conn, 'request'):
                request = conn.request
                break

        if request and isinstance(request, WSGIRequest):
            return request.user if request.user.is_authenticated else None
    except Exception as e:
        logger.warning(f"Could not get current user: {str(e)}")
    return None


@receiver(pre_save)
def log_pre_save(sender, instance, **kwargs):
    if sender.__name__ in ['Brand', 'CarModel', 'BodyType', 'Car', 'Statistic', 'AuditLog']:
        try:
            if instance.pk:
                old = sender.objects.get(pk=instance.pk)
                changes = {}

                for field in instance._meta.fields:
                    old_val = getattr(old, field.name)
                    new_val = getattr(instance, field.name)
                    if old_val != new_val:
                        changes[field.name] = {
                            'old': str(old_val),
                            'new': str(new_val)
                        }

                if changes:
                    user = get_current_user()
                    with transaction.atomic():
                        AuditLog.objects.create(
                            model_name=sender.__name__,
                            object_id=instance.pk,
                            action='U',
                            changes=changes,
                            user=user
                        )
                    logger.info(f"Changes detected in {sender.__name__} ID {instance.pk}")
        except sender.DoesNotExist:
            pass
        except Exception as e:
            logger.error(f"Error in pre_save audit for {sender.__name__}: {str(e)}")


@receiver(post_save)
def log_post_save(sender, instance, created, **kwargs):
    if sender.__name__ in ['Brand', 'CarModel', 'BodyType', 'Car', 'Statistic', 'AuditLog']:
        try:
            if created:
                user = get_current_user()
                with transaction.atomic():
                    AuditLog.objects.create(
                        model_name=sender.__name__,
                        object_id=instance.pk,
                        action='C',
                        changes={'created': True},
                        user=user
                    )
                logger.info(f"New {sender.__name__} created with ID {instance.pk}")
        except Exception as e:
            logger.error(f"Error in post_save audit for {sender.__name__}: {str(e)}")


@receiver(pre_delete)
def log_pre_delete(sender, instance, **kwargs):
    if sender.__name__ in ['Brand', 'CarModel', 'BodyType', 'Car', 'Statistic', 'AuditLog']:
        try:
            user = get_current_user()
            with transaction.atomic():
                AuditLog.objects.create(
                    model_name=sender.__name__,
                    object_id=instance.pk,
                    action='D',
                    changes={'deleted': True},
                    user=user
                )
            logger.info(f"{sender.__name__} with ID {instance.pk} deleted")
        except Exception as e:
            logger.error(f"Error in pre_delete audit for {sender.__name__}: {str(e)}")