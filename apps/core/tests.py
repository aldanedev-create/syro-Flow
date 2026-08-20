from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings

from apps.core.models import SiteSettings


class SiteSettingsTest(TestCase):
    """Test cases for SiteSettings model"""
    
    def test_site_settings_creation(self):
        """Test that site settings can be created"""
        settings = SiteSettings.get_solo()
        self.assertEqual(settings.site_name, 'Syro Flow')
        self.assertIsNotNone(settings.site_description)
    
    def test_site_settings_singleton(self):
        """Test that only one SiteSettings instance exists"""
        settings1 = SiteSettings.get_solo()
        with self.assertRaises(ValueError):
            # Trying to create another instance should fail
            SiteSettings.objects.create(site_name='Test')
    
    def test_site_settings_update(self):
        """Test that site settings can be updated"""
        settings = SiteSettings.get_solo()
        new_name = 'Updated Syro Flow'
        settings.site_name = new_name
        settings.save()
        
        updated = SiteSettings.get_solo()
        self.assertEqual(updated.site_name, new_name)


class CoreViewsTest(TestCase):
    """Test cases for core views"""
    
    def test_homepage_view(self):
        """Test that homepage loads correctly"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home/index.html')
    
    def test_homepage_context(self):
        """Test that homepage has required context variables"""
        response = self.client.get(reverse('home'))
        self.assertIn('site_name', response.context)
        self.assertIn('site_description', response.context)
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b'OK')
    
    def test_robots_txt(self):
        """Test robots.txt endpoint"""
        response = self.client.get('/robots.txt')
        self.assertEqual(response.status_code, 200)
        self.assertIn('User-Agent: *', response.content.decode())
        self.assertIn('Disallow: /admin/', response.content.decode())
    
    def test_404_page(self):
        """Test custom 404 page"""
        response = self.client.get('/this-page-does-not-exist/')
        self.assertEqual(response.status_code, 404)
        self.assertTemplateUsed(response, '404.html')


class ContextProcessorsTest(TestCase):
    """Test cases for context processors"""
    
    def test_site_settings_processor(self):
        """Test that site_settings context processor works"""
        response = self.client.get(reverse('home'))
        self.assertIn('site_name', response.context)
        self.assertIn('site_description', response.context)
    
    def test_navigation_processor(self):
        """Test that navigation context processor works"""
        response = self.client.get(reverse('home'))
        self.assertIn('nav_pages', response.context)
        self.assertIn('nav_categories', response.context)