from django.db import models
from django.db.models import F
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.timezone import now
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from apps.media_library.models import Media


class Category(models.Model):
    """Category model for organizing posts"""
    
    name = models.CharField(max_length=100, verbose_name=_('Name'))
    slug = models.SlugField(max_length=100, unique=True, verbose_name=_('Slug'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('posts:category', kwargs={'slug': self.slug})
    
    @property
    def published_post_count(self):
        """Number of published posts in this category"""
        return self.posts.filter(status='published').count()


class Tag(models.Model):
    """Tag model for tagging posts"""
    
    name = models.CharField(max_length=50, verbose_name=_('Name'))
    slug = models.SlugField(max_length=50, unique=True, verbose_name=_('Slug'))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('posts:tag', kwargs={'slug': self.slug})


class Post(models.Model):
    """Post model for blog/content management"""
    
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    )
    
    # Core fields
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    slug = models.SlugField(max_length=200, unique=True, verbose_name=_('Slug'))
    content = models.TextField(verbose_name=_('Content'))
    excerpt = models.TextField(blank=True, max_length=500, verbose_name=_('Excerpt'))
    
    # Relationships
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name=_('Category')
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name='posts',
        verbose_name=_('Tags')
    )
    featured_image = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name=_('Featured Image')
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name=_('Author')
    )
    
    # Status fields
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        verbose_name=_('Status')
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Published At')
    )
    
    # Metadata
    view_count = models.PositiveIntegerField(default=0, verbose_name=_('View Count'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
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
    
    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ['-published_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Auto-generate slug and set published_at when publishing"""
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 2
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
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
        
        # Set published_at when status changes to published
        if self.status == 'published' and not self.published_at:
            self.published_at = now()
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """URL for this post"""
        return reverse('posts:detail', kwargs={'slug': self.slug})
    
    def increment_view_count(self):
        """Increment the view count"""
        type(self).objects.filter(pk=self.pk).update(view_count=F('view_count') + 1)
        self.refresh_from_db(fields=['view_count'])
    
    def get_reading_time(self):
        """Estimate reading time in minutes"""
        # Average reading speed: 200 words per minute
        import re
        word_count = len(re.findall(r'\w+', self.content))
        minutes = max(1, round(word_count / 200))
        return minutes
    
    def get_next_post(self):
        """Get the next published post by date"""
        return Post.objects.filter(
            status='published',
            published_at__gt=self.published_at
        ).order_by('published_at').first()
    
    def get_previous_post(self):
        """Get the previous published post by date"""
        return Post.objects.filter(
            status='published',
            published_at__lt=self.published_at
        ).order_by('-published_at').first()
    
    @property
    def is_published(self):
        """Check if post is published"""
        return self.status == 'published' and self.published_at is not None
    
    @classmethod
    def published(cls):
        """Get all published posts"""
        return cls.objects.filter(status='published')
    
    def get_featured_image_url(self):
        """Get the URL of the featured image"""
        if self.featured_image and self.featured_image.file:
            return self.featured_image.file.url
        return None
