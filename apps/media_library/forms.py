from django import forms
from django.core.exceptions import ValidationError
from .models import Media, MediaCategory
from .validators import validate_file_size, validate_file_type, validate_image_dimensions, validate_file_content


class MediaUploadForm(forms.ModelForm):
    """Form for uploading media files"""
    
    categories = forms.ModelMultipleChoiceField(
        queryset=MediaCategory.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Media
        fields = ('file', 'title', 'alt_text', 'caption', 'description', 'categories')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'alt_text': forms.TextInput(attrs={'class': 'form-control'}),
            'caption': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set required fields
        self.fields['title'].required = False
        self.fields['title'].help_text = 'Leave blank to use filename'
        
        # Help texts
        self.fields['alt_text'].help_text = 'Alternative text for accessibility'
        self.fields['caption'].help_text = 'Caption displayed below the image'
    
    def clean_file(self):
        """Validate uploaded file"""
        file = self.cleaned_data.get('file')
        if file:
            validate_file_size(file)
            validate_file_type(file)
            validate_file_content(file)
            validate_image_dimensions(file)  # Optional, only for images
        return file
    
    def clean_title(self):
        """Auto-generate title from filename if not provided"""
        title = self.cleaned_data.get('title')
        if not title and self.cleaned_data.get('file'):
            # Use filename without extension as title
            filename = self.cleaned_data['file'].name
            title = filename.split('.')[0]
            # Replace underscores and dashes with spaces
            title = title.replace('_', ' ').replace('-', ' ')
            # Capitalize words
            title = ' '.join(word.capitalize() for word in title.split())
        return title or 'Untitled'


class MediaCategoryForm(forms.ModelForm):
    """Form for creating/editing media categories"""
    
    class Meta:
        model = MediaCategory
        fields = ('name', 'slug', 'description')
    
    def clean_slug(self):
        """Validate slug is unique"""
        from django.utils.text import slugify
        slug = self.cleaned_data.get('slug')
        if not slug:
            slug = slugify(self.cleaned_data.get('name', ''))
        
        queryset = MediaCategory.objects.filter(slug=slug)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise ValidationError('A category with this slug already exists.')
        
        return slug


class MediaFilterForm(forms.Form):
    """Form for filtering media items"""
    
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search media...'
        })
    )
    
    media_type = forms.ChoiceField(
        choices=[('', 'All Types')] + list(Media.MEDIA_TYPES),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    category = forms.ModelChoiceField(
        queryset=MediaCategory.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    sort_by = forms.ChoiceField(
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('title', 'Alphabetical'),
            ('-file_size', 'Largest First'),
        ],
        initial='-created_at',
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
