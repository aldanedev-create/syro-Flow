from django.apps import AppConfig


class PagesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.pages'
    label = 'pages'
    verbose_name = 'Pages'
    
    def ready(self):
        """Import signals when app is ready"""
        # import apps.pages.signals
        pass