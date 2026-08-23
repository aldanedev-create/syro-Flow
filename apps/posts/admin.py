from django.contrib import admin
from django.utils.html import format_html
from django.utils.timezone import now
from .models import Post, Category, Tag


class PostAdmin(admin.ModelAdmin):
    """Admin configuration for Post model"""
    
    list_display = (
        'title', 
        'category', 
        'status', 
        'author', 
        'published_at',
        'view_count',
        'featured_image_preview'
    )
    list_filter = ('status', 'category', 'created_at', 'published_at', 'author')
    search_fields = ('title', 'content', 'excerpt', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('view_count', 'created_at', 'updated_at', 'featured_image_preview')
    date_hierarchy = 'published_at'
    ordering = ('-published_at',)
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'category', 'tags')
        }),
        ('Media', {
            'fields': ('featured_image', 'featured_image_preview'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('status', 'author', 'published_at')
        }),
        ('Metadata', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def featured_image_preview(self, obj):
        """Display thumbnail in admin list"""
        if obj.featured_image:
            return format_html(
                '<img src="{}" width="100" height="100" style="object-fit: cover;" />',
                obj.featured_image.file.url
            )
        return 'No Image'
    featured_image_preview.short_description = 'Image Preview'
    
    def save_model(self, request, obj, form, change):
        """Auto-set author and published_at when publishing"""
        if not obj.author:
            obj.author = request.user
        if obj.status == 'published' and not obj.published_at:
            obj.published_at = now()
        if obj.status == 'draft':
            obj.published_at = None
        super().save_model(request, obj, form, change)
    
    actions = ['publish_posts', 'unpublish_posts']
    
    def publish_posts(self, request, queryset):
        """Bulk publish selected posts"""
        updated = queryset.update(status='published', published_at=now())
        self.message_user(request, f'{updated} posts published successfully.')
    publish_posts.short_description = 'Publish selected posts'
    
    def unpublish_posts(self, request, queryset):
        """Bulk unpublish selected posts"""
        updated = queryset.update(status='draft', published_at=None)
        self.message_user(request, f'{updated} posts unpublished successfully.')
    unpublish_posts.short_description = 'Unpublish selected posts'


class CategoryAdmin(admin.ModelAdmin):
    """Admin configuration for Category model"""
    
    list_display = ('name', 'slug', 'post_count', 'description')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('post_count',)
    
    def post_count(self, obj):
        """Count posts in this category"""
        return obj.posts.filter(status='published').count()
    post_count.short_description = 'Published Posts'


class TagAdmin(admin.ModelAdmin):
    """Admin configuration for Tag model"""
    
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


# Register models with admin
admin.site.register(Post, PostAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)