from django import forms
from django.core.validators import MinValueValidator
from .models import DonationTransaction, DonationSettings, DonationGoal


class DonationForm(forms.ModelForm):
    """Form for making a donation"""
    
    amount = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'step': '0.01',
            'placeholder': '0.00'
        })
    )
    
    donor_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your full name'
        })
    )
    
    donor_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com'
        })
    )
    
    donor_phone = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+1234567890'
        })
    )
    
    payment_method = forms.ChoiceField(
        choices=DonationTransaction.PAYMENT_METHODS,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    is_anonymous = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    message = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Leave a message (optional)'
        })
    )
    
    class Meta:
        model = DonationTransaction
        fields = (
            'donor_name', 'donor_email', 'donor_phone',
            'amount', 'currency', 'payment_method',
            'is_anonymous', 'message'
        )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set default currency from settings
        settings_obj = DonationSettings.get_solo()
        if settings_obj:
            self.fields['currency'].initial = settings_obj.currency
        
        # Add help texts
        self.fields['donor_name'].help_text = 'Your full name'
        self.fields['amount'].help_text = 'Minimum donation: $0.01'
        self.fields['is_anonymous'].help_text = 'Check to remain anonymous'
    
    def clean_amount(self):
        """Validate amount is within reasonable bounds"""
        amount = self.cleaned_data.get('amount')
        if amount > 1000000:
            raise forms.ValidationError(
                'Amount exceeds maximum allowed donation.'
            )
        return amount


class DonationSettingsForm(forms.ModelForm):
    """Form for updating donation settings"""
    
    class Meta:
        model = DonationSettings
        fields = (
            'bank_name', 'account_name', 'account_number',
            'branch', 'currency', 'payment_methods',
            'mobile_money_number', 'paypal_email',
            'stripe_public_key', 'donation_message',
            'funds_usage', 'impact_stories', 'is_active',
            'cta_text', 'cta_url'
        )
        widgets = {
            'donation_message': forms.Textarea(attrs={'rows': 5}),
            'funds_usage': forms.Textarea(attrs={'rows': 5}),
            'impact_stories': forms.Textarea(attrs={'rows': 5}),
        }


class DonationGoalForm(forms.ModelForm):
    """Form for creating/editing donation goals"""
    
    class Meta:
        model = DonationGoal
        fields = (
            'title', 'description', 'target_amount',
            'currency', 'start_date', 'end_date',
            'is_active', 'featured_image'
        )
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', 'End date must be after start date.')
        
        return cleaned_data


class TransactionFilterForm(forms.Form):
    """Form for filtering transactions in admin"""
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + list(DonationTransaction.STATUS_CHOICES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    payment_method = forms.ChoiceField(
        choices=[('', 'All Methods')] + list(DonationTransaction.PAYMENT_METHODS),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search donor or transaction ID'
        })
    )