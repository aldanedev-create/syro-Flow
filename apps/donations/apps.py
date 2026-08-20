from django.apps import AppConfig


class DonationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.donations'
    label = 'donations'
    verbose_name = 'Donations'
    
    def ready(self):
        """Import signals when app is ready"""
        # import apps.donations.signals
        pass