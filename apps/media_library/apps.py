from django.apps import AppConfig


class MediaLibraryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.media_library'
    label = 'media_library'
    verbose_name = 'Media Library'
    
    def ready(self):
        """Import signals when app is ready"""
        # import apps.media_library.signals
        pass