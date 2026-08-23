from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Page, PageSection
from .forms import PageForm


class PageAdmin(admin.ModelAdmin):
    """Admin configuration for Page model"""
    
    form = PageForm
    list_display = (
        'title',
        'slug',
        'status',
        'created_at',
        'updated_at',
        'is_published_display'
    )
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('title',)
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'content', 'excerpt')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('SEO', {
            'fields': ('seo_title', 'seo_description'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def is_published_display(self, obj):
        """Display published status with color indicator"""
        if obj.status == 'published':
            return mark_safe('<span style="color: green;">\u2713 Published</span>')
        return mark_safe('<span style="color: orange;">\u2717 Draft</span>')
    is_published_display.short_description = 'Published'
    
    def save_model(self, request, obj, form, change):
        """Set default status if not set"""
        if not obj.pk:
            obj.status = obj.status or 'draft'
        super().save_model(request, obj, form, change)
    
    actions = ['publish_pages', 'unpublish_pages']
    
    def publish_pages(self, request, queryset):
        """Bulk publish selected pages"""
        updated = queryset.update(status='published')
        self.message_user(request, f'{updated} pages published successfully.')
    publish_pages.short_description = 'Publish selected pages'
    
    def unpublish_pages(self, request, queryset):
        """Bulk unpublish selected pages"""
        updated = queryset.update(status='draft')
        self.message_user(request, f'{updated} pages unpublished successfully.')
    unpublish_pages.short_description = 'Unpublish selected pages'


# Register models with admin
admin.site.register(Page, PageAdmin)


class PageSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'page', 'order')
    list_filter = ('page',)
    search_fields = ('title', 'content', 'page__title')
    ordering = ('page', 'order')


admin.site.register(PageSection, PageSectionAdmin)
