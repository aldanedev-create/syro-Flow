from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class Page(models.Model):
    """Page model for static/permanent pages"""
    
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('published', _('Published')),
    )
    
    # Core fields
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_('Slug'))
    content = models.TextField(verbose_name=_('Content'))
    excerpt = models.TextField(
        blank=True,
        max_length=500,
        verbose_name=_('Excerpt')
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        blank=True,
        verbose_name=_('Status')
    )
    
    # SEO fields
    seo_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('SEO Title')
    )
    seo_description = models.TextField(
        blank=True,
        max_length=300,
        verbose_name=_('SEO Description')
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')
        ordering = ['title']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Auto-generate slug if not provided"""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 2
            while Page.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = slug
        
        # Auto-generate excerpt from content if not provided.
        # Always end with '...' since this is a generated preview, not the
        # full content, even when the content itself is short.
        if not self.excerpt and self.content:
            import re
            plain_text = re.sub(r'<[^>]+>', '', self.content)
            self.excerpt = plain_text[:300].rstrip() + '...'
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """URL for this page"""
        return reverse('pages:detail', kwargs={'slug': self.slug})
    
    @property
    def is_published(self):
        """Check if page is published"""
        return self.status == 'published'
    
    @classmethod
    def published(cls):
        """Get all published pages"""
        return cls.objects.filter(status='published')
    
    def get_reading_time(self):
        """Estimate reading time in minutes"""
        import re
        word_count = len(re.findall(r'\w+', self.content))
        minutes = max(1, round(word_count / 200))
        return minutes


class PageSection(models.Model):
    """Optional: Sections within a page (for complex pages like About)"""
    
    page = models.ForeignKey(
        Page,
        on_delete=models.CASCADE,
        related_name='sections',
        verbose_name=_('Page')
    )
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    content = models.TextField(verbose_name=_('Content'))
    order = models.PositiveIntegerField(default=0, verbose_name=_('Order'))
    
    class Meta:
        verbose_name = _('Page Section')
        verbose_name_plural = _('Page Sections')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.page.title} - {self.title}"