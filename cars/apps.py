from django.apps import AppConfig


class CarsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cars'

    def ready(self):
        # Регистрируем сигналы при старте приложения
        import cars.signals.audit_signals  # noqa