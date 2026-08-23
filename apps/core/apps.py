from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core'
    label = 'core'
    verbose_name = 'Core'

    def ready(self):
        """Import signals when app is ready"""
        # import apps.core.signals  # Uncomment if you have signals
        pass