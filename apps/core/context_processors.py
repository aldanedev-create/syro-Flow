"""
Context processors that make variables available to all templates
"""
from django.conf import settings
from apps.core.models import SiteSettings


def site_settings(request):
    """
    Add site-wide settings to all template contexts.
    This makes settings like site_name, site_description available everywhere.
    """
    try:
        settings_obj = SiteSettings.get_solo()
    except SiteSettings.DoesNotExist:
        settings_obj = None
    
    return {
        'site_name': settings.SITE_NAME if not settings_obj else settings_obj.site_name,
        'site_description': settings.SITE_DESCRIPTION if not settings_obj else settings_obj.site_description,
        'site_settings': settings_obj,
        'site_url': settings.SITE_URL,
        'debug': settings.DEBUG,
    }


def navigation(request):
    """
    Add navigation menu items to all templates
    """
    from apps.pages.models import Page
    from apps.posts.models import Category
    
    # Get published pages for navigation
    pages = Page.objects.filter(status='published').order_by('title')
    
    # Get all categories with at least one published post
    categories = Category.objects.filter(
        posts__status='published'
    ).distinct().order_by('name')
    
    return {
        'nav_pages': pages,
        'nav_categories': categories,
    }