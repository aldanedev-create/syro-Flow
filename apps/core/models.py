from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class SiteSettings(models.Model):
    """Site-wide settings that can be managed from admin"""
    
    site_name = models.CharField(
        max_length=200,
        default='Syro Flow',
        verbose_name=_('Site Name')
    )
    site_description = models.TextField(
        blank=True,
        verbose_name=_('Site Description')
    )
    site_logo = models.ImageField(
        upload_to='site/',
        blank=True,
        null=True,
        verbose_name=_('Site Logo')
    )
    favicon = models.ImageField(
        upload_to='site/',
        blank=True,
        null=True,
        verbose_name=_('Favicon')
    )
    
    # Footer settings
    footer_text = models.TextField(
        blank=True,
        verbose_name=_('Footer Text')
    )
    copyright_text = models.CharField(
        max_length=200,
        default='© 2024 Syro Flow. All rights reserved.',
        verbose_name=_('Copyright Text')
    )
    
    # Social Media
    facebook_url = models.URLField(blank=True, verbose_name=_('Facebook URL'))
    twitter_url = models.URLField(blank=True, verbose_name=_('Twitter URL'))
    instagram_url = models.URLField(blank=True, verbose_name=_('Instagram URL'))
    youtube_url = models.URLField(blank=True, verbose_name=_('YouTube URL'))
    
    # Contact
    email = models.EmailField(blank=True, verbose_name=_('Contact Email'))
    phone = models.CharField(max_length=20, blank=True, verbose_name=_('Phone Number'))
    address = models.TextField(blank=True, verbose_name=_('Address'))
    
    # Meta
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_('Meta Keywords')
    )
    meta_description = models.TextField(
        blank=True,
        verbose_name=_('Meta Description')
    )
    
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Site Settings')
        verbose_name_plural = _('Site Settings')
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and SiteSettings.objects.exists():
            raise ValueError('There can only be one SiteSettings instance')
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls):
        """Get the single instance, create if it doesn't exist"""
        instance, created = cls.objects.get_or_create(pk=1)
        if created:
            instance.save()
        return instance