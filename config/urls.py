"""
URL configuration for Syro Flow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from apps.posts.models import Post
from apps.pages.models import Page


class PostSitemap:
    protocol = 'https'

    def items(self):
        return Post.published()

    def location(self, item):
        return item.get_absolute_url()

    def lastmod(self, item):
        return item.updated_at


class PageSitemap:
    protocol = 'https'

    def items(self):
        return Page.published()

    def location(self, item):
        return item.get_absolute_url()

    def lastmod(self, item):
        return item.updated_at


sitemaps = {'posts': PostSitemap(), 'pages': PageSitemap()}

# Import views from apps
from apps.core import views as core_views

urlpatterns = [
    # Admin
    path(settings.ADMIN_URL, admin.site.urls),
    
    # Core/Home
    path('', core_views.home, name='home'),
    path('health/', core_views.health_check, name='health_check'),
    path('robots.txt', core_views.robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    
    # Apps
    path('posts/', include('apps.posts.urls')),
    path('pages/', include('apps.pages.urls')),
    path('gallery/', include('apps.media_library.urls')),
    path('donations/', include('apps.donations.urls')),
    path('rebuke/', include('apps.rebuke.urls')),
    
    # API (Optional - if you want to expose REST API)
    # path('api/', include('apps.api.urls')),
    
    # Sitemap (Optional)
    # path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar (optional)
    # if 'debug_toolbar' in settings.INSTALLED_APPS:
    #     import debug_toolbar
    #     urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]

# Custom error handlers
handler404 = 'apps.core.views.custom_404'
handler500 = 'apps.core.views.custom_500'
