from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .models import DonationSettings, DonationTransaction, DonationGoal


class DonationSettingsAdmin(admin.ModelAdmin):
    """Admin configuration for DonationSettings model"""
    
    list_display = (
        'bank_name',
        'account_name',
        'currency',
        'updated_at_display',
        'status_display'
    )
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Bank Details', {
            'fields': (
                'bank_name',
                'account_name',
                'account_number',
                'branch',
                'currency'
            )
        }),
        ('Payment Methods', {
            'fields': (
                'payment_methods',
                'mobile_money_number',
                'paypal_email',
                'stripe_public_key',
            ),
            'classes': ('collapse',)
        }),
        ('Content', {
            'fields': (
                'donation_message',
                'funds_usage',
                'impact_stories'
            )
        }),
        ('Display Settings', {
            'fields': (
                'is_active',
                'featured_image',
                'cta_text',
                'cta_url'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def updated_at_display(self, obj):
        """Display updated at in a readable format"""
        return obj.updated_at.strftime('%Y-%m-%d %H:%M')
    updated_at_display.short_description = 'Last Updated'
    
    def status_display(self, obj):
        """Display active status with color indicator"""
        if obj.is_active:
            return mark_safe('<span style="color: green; font-weight: bold;">\u2713 Active</span>')
        return mark_safe('<span style="color: red; font-weight: bold;">\u2717 Inactive</span>')
    status_display.short_description = 'Status'
    
    def has_add_permission(self, request):
        """Only allow one instance"""
        if DonationSettings.objects.exists():
            return False
        return True
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of settings"""
        return False


class DonationTransactionAdmin(admin.ModelAdmin):
    """Admin configuration for DonationTransaction model"""
    
    list_display = (
        'donor_name',
        'amount_display',
        'currency_display',
        'payment_method',
        'status_display',
        'created_at'
    )
    list_filter = (
        'payment_method',
        'status',
        'currency',
        'created_at'
    )
    search_fields = (
        'donor_name',
        'donor_email',
        'transaction_id',
        'message'
    )
    readonly_fields = (
        'transaction_id',
        'created_at',
        'updated_at',
        'payment_response'
    )
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Donor Information', {
            'fields': (
                'donor_name',
                'donor_email',
                'donor_phone'
            )
        }),
        ('Transaction Details', {
            'fields': (
                'amount',
                'currency',
                'payment_method',
                'transaction_id',
                'status'
            )
        }),
        ('Additional Info', {
            'fields': (
                'message',
                'is_anonymous',
                'payment_response'
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def amount_display(self, obj):
        """Display amount with currency symbol"""
        return f"{obj.currency} {obj.amount}"
    amount_display.short_description = 'Amount'
    
    def currency_display(self, obj):
        """Display currency"""
        return obj.get_currency_display()
    currency_display.short_description = 'Currency'
    
    def status_display(self, obj):
        """Display status with color indicator"""
        colors = {
            'pending': 'orange',
            'completed': 'green',
            'failed': 'red',
            'refunded': 'gray'
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    actions = ['mark_as_completed', 'mark_as_refunded']
    
    def mark_as_completed(self, request, queryset):
        """Mark selected transactions as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} transactions marked as completed.')
    mark_as_completed.short_description = 'Mark as completed'
    
    def mark_as_refunded(self, request, queryset):
        """Mark selected transactions as refunded"""
        updated = queryset.update(status='refunded')
        self.message_user(request, f'{updated} transactions marked as refunded.')
    mark_as_refunded.short_description = 'Mark as refunded'


class DonationGoalAdmin(admin.ModelAdmin):
    """Admin configuration for DonationGoal model"""
    
    list_display = (
        'title',
        'target_amount_display',
        'raised_amount_display',
        'progress_display',
        'start_date',
        'end_date',
        'is_active_display'
    )
    list_filter = ('is_active', 'start_date', 'end_date')
    search_fields = ('title', 'description')
    readonly_fields = ('raised_amount', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Goal Details', {
            'fields': (
                'title',
                'description',
                'target_amount',
                'raised_amount',
                'currency'
            )
        }),
        ('Dates', {
            'fields': (
                'start_date',
                'end_date'
            )
        }),
        ('Status', {
            'fields': (
                'is_active',
                'featured_image'
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def target_amount_display(self, obj):
        """Display target amount with currency"""
        return f"{obj.currency} {obj.target_amount}"
    target_amount_display.short_description = 'Target'
    
    def raised_amount_display(self, obj):
        """Display raised amount with currency"""
        return f"{obj.currency} {obj.raised_amount}"
    raised_amount_display.short_description = 'Raised'
    
    def progress_display(self, obj):
        """Display progress bar"""
        if obj.target_amount > 0:
            percentage = (obj.raised_amount / obj.target_amount) * 100
            percentage = min(percentage, 100)
            return format_html(
                '<div style="width: 100%; background: #e9ecef; border-radius: 4px; overflow: hidden;">'
                '<div style="width: {}%; background: #28a745; padding: 2px 0; text-align: center; color: white; font-size: 12px;">{:.1f}%</div>'
                '</div>',
                percentage, percentage
            )
        return '0%'
    progress_display.short_description = 'Progress'
    
    def is_active_display(self, obj):
        """Display active status with color indicator"""
        if obj.is_active:
            return mark_safe('<span style="color: green; font-weight: bold;">\u2713 Active</span>')
        return mark_safe('<span style="color: gray; font-weight: bold;">\u2717 Inactive</span>')
    is_active_display.short_description = 'Active'


# Register models with admin
admin.site.register(DonationSettings, DonationSettingsAdmin)
admin.site.register(DonationTransaction, DonationTransactionAdmin)
admin.site.register(DonationGoal, DonationGoalAdmin)