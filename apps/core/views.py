from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from django.conf import settings

from apps.posts.models import Post


def home(request):
    """Homepage view - shows recent published posts"""
    recent_posts = Post.objects.filter(
        status='published'
    ).order_by('-published_at')[:6]
    
    context = {
        'recent_posts': recent_posts,
        'site_name': settings.SITE_NAME,
        'site_description': settings.SITE_DESCRIPTION,
    }
    return render(request, 'home/index.html', context)


def custom_404(request, exception):
    """Custom 404 error handler"""
    return render(request, '404.html', status=404)


def custom_500(request):
    """Custom 500 error handler"""
    return render(request, '500.html', status=500)


# Health check endpoint for Vercel
def health_check(request):
    """Health check endpoint for monitoring"""
    return HttpResponse('OK')


# Robots.txt
def robots_txt(request):
    """Robots.txt for search engine crawlers"""
    lines = [
        'User-Agent: *',
        'Disallow: /admin/',
        'Disallow: /media/',
        'Allow: /',
        f'Sitemap: {settings.SITE_URL}/sitemap.xml',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')