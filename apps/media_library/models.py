import os
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile


class MediaCategory(models.Model):
    """Category for organizing media files"""
    
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Slug'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    class Meta:
        verbose_name = _('Media Category')
        verbose_name_plural = _('Media Categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Media(models.Model):
    """Media model for managing uploaded files"""
    
    MEDIA_TYPES = (
        ('image', _('Image')),
        ('video', _('Video')),
        ('document', _('Document')),
        ('audio', _('Audio')),
        ('other', _('Other')),
    )
    
    # File
    file = models.FileField(
        upload_to='uploads/%Y/%m/%d/',
        verbose_name=_('File'),
        validators=[FileExtensionValidator(
            allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'pdf', 'doc', 'docx', 'mp4', 'mp3']
        )]
    )
    
    # Metadata
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    alt_text = models.CharField(max_length=200, blank=True, verbose_name=_('Alt Text'))
    caption = models.TextField(blank=True, verbose_name=_('Caption'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    # Organization
    categories = models.ManyToManyField(
        MediaCategory,
        blank=True,
        related_name='media',
        verbose_name=_('Categories')
    )
    media_type = models.CharField(
        max_length=20,
        choices=MEDIA_TYPES,
        default='image',
        verbose_name=_('Media Type')
    )
    
    # Upload info
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploaded_media',
        verbose_name=_('Uploaded By')
    )
    
    # File metadata
    file_size = models.PositiveIntegerField(default=0, verbose_name=_('File Size (bytes)'))
    width = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Width'))
    height = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Height'))
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Media')
        verbose_name_plural = _('Media')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['media_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['uploaded_by']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Set file metadata on save"""
        if self.file:
            # Set file size
            if not self.file_size:
                self.file_size = self.file.size
            
            # Set media type based on file extension
            if not self.media_type or self.media_type == 'other':
                self.media_type = self.detect_media_type()
            
            # Get image dimensions if it's an image
            if self.is_image() and not (self.width and self.height):
                self.set_image_dimensions()
        
        super().save(*args, **kwargs)
    
    def detect_media_type(self):
        """Detect media type from file extension"""
        ext = os.path.splitext(self.file.name)[1].lower()
        
        image_exts = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg', '.bmp', '.ico']
        video_exts = ['.mp4', '.webm', '.ogg', '.mov', '.avi']
        audio_exts = ['.mp3', '.wav', '.ogg', '.m4a']
        document_exts = ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt']
        
        if ext in image_exts:
            return 'image'
        elif ext in video_exts:
            return 'video'
        elif ext in audio_exts:
            return 'audio'
        elif ext in document_exts:
            return 'document'
        else:
            return 'other'
    
    def is_image(self):
        """Check if file is an image"""
        return self.media_type == 'image' or self.detect_media_type() == 'image'
    
    def set_image_dimensions(self):
        """Set width and height for image files"""
        try:
            if self.file and self.is_image():
                img = Image.open(self.file)
                self.width = img.width
                self.height = img.height
        except Exception:
            # If we can't read image dimensions, just pass
            pass
    
    def get_file_size_display(self):
        """Get human readable file size"""
        size = self.file_size
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        elif size < 1024 * 1024 * 1024:
            return f"{size / (1024 * 1024):.1f} MB"
        else:
            return f"{size / (1024 * 1024 * 1024):.1f} GB"
    
    def get_absolute_url(self):
        """Get URL for the media file"""
        if self.file:
            return self.file.url
        return None
    
    def get_thumbnail_url(self):
        """Get thumbnail URL (for images)"""
        if self.is_image() and self.file:
            # Return original for now, could use a thumbnail generation library
            return self.file.url
        return None
    
    @classmethod
    def get_used_media(cls):
        """Get media that is used in posts"""
        return cls.objects.filter(posts__isnull=False).distinct()
    
    @classmethod
    def get_unused_media(cls):
        """Get media that is not used in any post"""
        return cls.objects.filter(posts__isnull=True)