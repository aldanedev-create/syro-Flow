from django import forms
from django.core.validators import EmailValidator
from django.utils.text import slugify
from .models import Page, PageSection


class ContactForm(forms.Form):
    """Contact form for sending messages"""
    
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your full name',
            'required': True,
        }),
        error_messages={
            'required': 'Please enter your name.',
            'max_length': 'Name is too long (max 100 characters).',
        }
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your@email.com',
            'required': True,
        }),
        error_messages={
            'required': 'Please enter your email address.',
            'invalid': 'Please enter a valid email address.',
        }
    )
    
    subject = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject (optional)',
        }),
        error_messages={
            'max_length': 'Subject is too long (max 200 characters).',
        }
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Your message...',
            'required': True,
        }),
        error_messages={
            'required': 'Please enter your message.',
        }
    )
    
    def clean_message(self):
        """Validate message length and content"""
        message = self.cleaned_data.get('message', '').strip()
        
        if len(message) < 10:
            raise forms.ValidationError(
                'Message is too short (minimum 10 characters).'
            )
        
        if len(message) > 5000:
            raise forms.ValidationError(
                'Message is too long (maximum 5000 characters).'
            )
        
        return message
    
    def clean_name(self):
        """Sanitize name"""
        name = self.cleaned_data.get('name', '').strip()
        
        # Remove any HTML tags
        import re
        name = re.sub(r'<[^>]+>', '', name)
        
        if len(name) < 2:
            raise forms.ValidationError(
                'Please enter your full name (minimum 2 characters).'
            )
        
        return name


class PageForm(forms.ModelForm):
    """Form for creating/editing pages"""
    
    class Meta:
        model = Page
        fields = (
            'title', 'slug', 'content', 'excerpt',
            'status', 'seo_title', 'seo_description'
        )
        widgets = {
            'content': forms.Textarea(attrs={'class': 'rich-text-editor'}),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Slug is optional on the form even though it's required on the
        # model - clean_slug() below auto-generates it from the title when
        # left blank, same as Page.save() does.
        self.fields['slug'].required = False
        
        # Add help texts
        self.fields['slug'].help_text = 'Leave blank to auto-generate from title'
        self.fields['excerpt'].help_text = 'A short summary of the page (max 500 characters)'
        self.fields['seo_title'].help_text = 'SEO title (max 200 characters)'
        self.fields['seo_description'].help_text = 'SEO meta description (max 300 characters)'
    
    def clean_slug(self):
        """Validate slug is unique"""
        slug = self.cleaned_data.get('slug')
        if not slug:
            slug = slugify(self.cleaned_data.get('title', ''))
        
        # Check if slug already exists (excluding this instance)
        queryset = Page.objects.filter(slug=slug)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError('A page with this slug already exists.')
        
        return slug


class PageSectionForm(forms.ModelForm):
    """Form for creating/editing page sections"""
    
    class Meta:
        model = PageSection
        fields = ('title', 'content', 'order')
        widgets = {
            'content': forms.Textarea(attrs={'class': 'rich-text-editor'}),
        }
    
    def clean_order(self):
        """Validate order is non-negative"""
        order = self.cleaned_data.get('order')
        if order < 0:
            raise forms.ValidationError('Order must be a positive number.')
        return order


class PageSectionInlineFormSet(forms.BaseInlineFormSet):
    """Formset for page sections inline editing"""
    
    def clean(self):
        """Ensure no duplicate order values"""
        orders = []
        for form in self.forms:
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                order = form.cleaned_data.get('order')
                if order in orders:
                    form.add_error('order', 'Duplicate order values are not allowed.')
                orders.append(order)