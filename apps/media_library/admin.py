from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .models import Media, MediaCategory


class MediaAdmin(admin.ModelAdmin):
    """Admin configuration for Media model"""
    
    list_display = (
        'title',
        'file_preview',
        'media_type',
        'file_size_display',
        'uploaded_by',
        'created_at',
        'is_used'
    )
    list_filter = ('media_type', 'created_at', 'uploaded_by', 'categories')
    search_fields = ('title', 'alt_text', 'caption', 'file')
    readonly_fields = ('file_size', 'file_size_display', 'file_preview', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('File Information', {
            'fields': ('file', 'file_preview', 'file_size_display')
        }),
        ('Metadata', {
            'fields': ('title', 'alt_text', 'caption', 'description')
        }),
        ('Organization', {
            'fields': ('categories', 'media_type')
        }),
        ('Upload Info', {
            'fields': ('uploaded_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def file_preview(self, obj):
        """Display thumbnail preview in admin"""
        if obj.file and obj.is_image():
            return format_html(
                '<img src="{}" width="150" height="150" style="object-fit: cover; border-radius: 4px;" />',
                obj.file.url
            )
        elif obj.file:
            return mark_safe('<span style="font-size: 2em; display: block;">\U0001F4C4</span>')
        return 'No File'
    file_preview.short_description = 'Preview'
    
    def file_size_display(self, obj):
        """Display file size in human readable format"""
        return obj.get_file_size_display()
    file_size_display.short_description = 'File Size'
    
    def is_used(self, obj):
        """Check if media is used in any post"""
        if obj.posts.exists():
            return format_html(
                '<span style="color: green;">✓ Used in {} post(s)</span>',
                obj.posts.count()
            )
        return mark_safe('<span style="color: gray;">\u2717 Not in use</span>')
    is_used.short_description = 'Usage'
    
    def save_model(self, request, obj, form, change):
        """Set uploaded_by when creating"""
        if not obj.pk:
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['delete_selected', 'mark_as_used']
    
    def mark_as_used(self, request, queryset):
        """Bulk mark media as used (for tracking)"""
        # This is just a placeholder - actual usage is tracked via relationships
        self.message_user(request, f'{queryset.count()} media items marked.')
    mark_as_used.short_description = 'Mark as used'


class MediaCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for MediaCategory model"""
    
    list_display = ('name', 'slug', 'media_count')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    
    def media_count(self, obj):
        """Count media in this category"""
        return obj.media_set.count()
    media_count.short_description = 'Media Count'


# Register models with admin
admin.site.register(Media, MediaAdmin)
admin.site.register(MediaCategory, MediaCategoryAdmin)