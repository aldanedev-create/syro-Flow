"""
Context processors that make variables available to all templates
"""
from django.conf import settings
from django.db import OperationalError, ProgrammingError
from apps.core.models import SiteSettings


def site_settings(request):
    """
    Add site-wide settings to all template contexts.
    This makes settings like site_name, site_description available everywhere.
    """
    try:
        settings_obj = SiteSettings.get_solo()
    except (ProgrammingError, OperationalError, SiteSettings.DoesNotExist):
        settings_obj = None

    return {
        'site_name': getattr(settings, 'SITE_NAME', '') if not settings_obj else settings_obj.site_name,
        'site_description': getattr(settings, 'SITE_DESCRIPTION', '') if not settings_obj else settings_obj.site_description,
        'site_settings': settings_obj,
        'site_url': getattr(settings, 'SITE_URL', ''),
        'debug': getattr(settings, 'DEBUG', False),
    }


def navigation(request):
    """
    Add navigation menu items to all templates
    """
    try:
        from apps.pages.models import Page
        from apps.posts.models import Category

        # list() forces immediate evaluation to catch missing database table errors here
        pages = list(Page.objects.filter(status='published').order_by('title'))
        categories = list(
            Category.objects.filter(posts__status='published')
            .distinct()
            .order_by('name')
        )
    except (ProgrammingError, OperationalError):
        pages = []
        categories = []

    return {
        'nav_pages': pages,
        'nav_categories': categories,
    }