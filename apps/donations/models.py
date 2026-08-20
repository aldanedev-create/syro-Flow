from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.media_library.models import Media


class DonationSettings(models.Model):
    """Donation settings and information"""
    
    CURRENCY_CHOICES = (
        ('USD', _('USD - US Dollar')),
        ('EUR', _('EUR - Euro')),
        ('GBP', _('GBP - British Pound')),
        ('NGN', _('NGN - Nigerian Naira')),
        ('KES', _('KES - Kenyan Shilling')),
        ('ZAR', _('ZAR - South African Rand')),
        ('GHS', _('GHS - Ghanaian Cedi')),
        ('UGX', _('UGX - Ugandan Shilling')),
        ('TZS', _('TZS - Tanzanian Shilling')),
    )
    
    PAYMENT_METHODS = (
        ('bank_transfer', _('Bank Transfer')),
        ('mobile_money', _('Mobile Money')),
        ('paypal', _('PayPal')),
        ('stripe', _('Stripe')),
        ('cash', _('Cash')),
    )
    
    # Bank Details
    bank_name = models.CharField(max_length=100, verbose_name=_('Bank Name'))
    account_name = models.CharField(max_length=100, verbose_name=_('Account Name'))
    account_number = models.CharField(max_length=50, verbose_name=_('Account Number'))
    branch = models.CharField(max_length=100, blank=True, verbose_name=_('Branch'))
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD',
        verbose_name=_('Currency')
    )
    
    # Payment Methods
    payment_methods = models.CharField(
        max_length=200,
        choices=PAYMENT_METHODS,
        default='bank_transfer',
        blank=True,
        verbose_name=_('Payment Methods')
    )
    mobile_money_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('Mobile Money Number')
    )
    paypal_email = models.EmailField(blank=True, verbose_name=_('PayPal Email'))
    stripe_public_key = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_('Stripe Public Key')
    )
    
    # Content
    donation_message = models.TextField(
        blank=True,
        verbose_name=_('Donation Message'),
        help_text=_('Message displayed to donors')
    )
    funds_usage = models.TextField(
        blank=True,
        verbose_name=_('Funds Usage'),
        help_text=_('How donations will be used')
    )
    impact_stories = models.TextField(
        blank=True,
        verbose_name=_('Impact Stories'),
        help_text=_('Stories of how donations have helped')
    )
    
    # Display Settings
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    featured_image = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Featured Image')
    )
    cta_text = models.CharField(
        max_length=100,
        default='Donate Now',
        blank=True,
        verbose_name=_('CTA Text')
    )
    cta_url = models.URLField(blank=True, verbose_name=_('CTA URL'))
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Donation Settings')
        verbose_name_plural = _('Donation Settings')
    
    def __str__(self):
        return f"{self.bank_name} - {self.account_name}"
    
    def save(self, *args, **kwargs):
        """Ensure only one instance exists"""
        if not self.pk and DonationSettings.objects.exists():
            raise ValueError('There can only be one DonationSettings instance')
        super().save(*args, **kwargs)
    
    @classmethod
    def get_solo(cls):
        """Get the single instance, create if it doesn't exist"""
        instance, created = cls.objects.get_or_create(pk=1)
        if created:
            instance.save()
        return instance
    
    def get_currency_symbol(self):
        """Get currency symbol"""
        symbols = {
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'NGN': '₦',
            'KES': 'KSh',
            'ZAR': 'R',
            'GHS': '₵',
            'UGX': 'USh',
            'TZS': 'TSh',
        }
        return symbols.get(self.currency, self.currency)


class DonationTransaction(models.Model):
    """Track donation transactions"""
    
    STATUS_CHOICES = (
        ('pending', _('Pending')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('refunded', _('Refunded')),
    )
    
    PAYMENT_METHODS = (
        ('bank_transfer', _('Bank Transfer')),
        ('mobile_money', _('Mobile Money')),
        ('paypal', _('PayPal')),
        ('stripe', _('Stripe')),
        ('cash', _('Cash')),
    )
    
    CURRENCY_CHOICES = DonationSettings.CURRENCY_CHOICES
    
    # Donor Information
    donor_name = models.CharField(max_length=200, verbose_name=_('Donor Name'))
    donor_email = models.EmailField(blank=True, verbose_name=_('Donor Email'))
    donor_phone = models.CharField(max_length=50, blank=True, verbose_name=_('Donor Phone'))
    is_anonymous = models.BooleanField(default=False, verbose_name=_('Anonymous'))
    
    # Transaction Details
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name=_('Amount')
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD',
        verbose_name=_('Currency')
    )
    payment_method = models.CharField(
        max_length=50,
        choices=PAYMENT_METHODS,
        verbose_name=_('Payment Method')
    )
    transaction_id = models.CharField(
        max_length=200,
        unique=True,
        blank=True,
        verbose_name=_('Transaction ID')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status')
    )
    
    # Additional Info
    message = models.TextField(blank=True, verbose_name=_('Message'))
    payment_response = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('Payment Response')
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Donation Transaction')
        verbose_name_plural = _('Donation Transactions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['transaction_id']),
            models.Index(fields=['created_at']),
            models.Index(fields=['donor_email']),
        ]
    
    def __str__(self):
        return f"{self.donor_name} - {self.amount} {self.currency}"
    
    def generate_transaction_id(self):
        """Generate a unique transaction ID"""
        import uuid
        return f"SYRO-{uuid.uuid4().hex[:12].upper()}"
    
    def save(self, *args, **kwargs):
        """Generate transaction ID if not provided"""
        if not self.transaction_id:
            self.transaction_id = self.generate_transaction_id()
        super().save(*args, **kwargs)
    
    def get_amount_display(self):
        """Get amount with currency symbol"""
        return f"{self.currency} {self.amount}"


class DonationGoal(models.Model):
    """Track donation goals and campaigns"""
    
    CURRENCY_CHOICES = DonationSettings.CURRENCY_CHOICES
    
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    target_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name=_('Target Amount')
    )
    raised_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_('Raised Amount')
    )
    currency = models.CharField(
        max_length=3,
        choices=CURRENCY_CHOICES,
        default='USD',
        verbose_name=_('Currency')
    )
    
    start_date = models.DateField(verbose_name=_('Start Date'))
    end_date = models.DateField(blank=True, null=True, verbose_name=_('End Date'))
    
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    featured_image = models.ForeignKey(
        Media,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Featured Image')
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Donation Goal')
        verbose_name_plural = _('Donation Goals')
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    def get_progress_percentage(self):
        """Calculate progress percentage"""
        if self.target_amount > 0:
            percentage = (self.raised_amount / self.target_amount) * 100
            return min(percentage, 100)
        return 0
    
    def get_remaining_amount(self):
        """Calculate remaining amount to reach goal"""
        remaining = self.target_amount - self.raised_amount
        return max(remaining, 0)
    
    def is_completed(self):
        """Check if goal is completed"""
        return self.raised_amount >= self.target_amount
    
    def is_expired(self):
        """Check if goal is expired"""
        if self.end_date:
            return now().date() > self.end_date
        return False
    
    def add_donation(self, amount):
        """Add a donation to the raised amount"""
        self.raised_amount += amount
        self.save()