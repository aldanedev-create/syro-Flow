from django import forms
from django.utils.text import slugify
from .models import Post, Category, Tag


class PostSearchForm(forms.Form):
    """Search form for posts"""
    
    q = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'search-input',
            'placeholder': 'Search posts...',
            'type': 'search',
        })
    )


class PostForm(forms.ModelForm):
    """Form for creating/editing posts in admin"""
    
    class Meta:
        model = Post
        fields = (
            'title', 'slug', 'content', 'excerpt',
            'category', 'tags', 'featured_image',
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
        # left blank, same as Post.save() does.
        self.fields['slug'].required = False
        
        # Add help texts
        self.fields['slug'].help_text = 'Leave blank to auto-generate from title'
        self.fields['excerpt'].help_text = 'A short summary of the post (max 500 characters)'
        self.fields['seo_title'].help_text = 'SEO title (max 200 characters)'
        self.fields['seo_description'].help_text = 'SEO meta description (max 300 characters)'
    
    def clean_slug(self):
        """Validate slug is unique"""
        slug = self.cleaned_data.get('slug')
        if not slug:
            slug = slugify(self.cleaned_data.get('title', ''))
        
        # Check if slug already exists (excluding this instance)
        queryset = Post.objects.filter(slug=slug)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError('A post with this slug already exists.')
        
        return slug


class CategoryForm(forms.ModelForm):
    """Form for creating/editing categories"""
    
    class Meta:
        model = Category
        fields = ('name', 'slug', 'description')
    
    def clean_slug(self):
        """Validate slug is unique"""
        slug = self.cleaned_data.get('slug')
        if not slug:
            slug = slugify(self.cleaned_data.get('name', ''))
        
        queryset = Category.objects.filter(slug=slug)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError('A category with this slug already exists.')
        
        return slug


class TagForm(forms.ModelForm):
    """Form for creating/editing tags"""
    
    class Meta:
        model = Tag
        fields = ('name', 'slug')
    
    def clean_slug(self):
        """Validate slug is unique"""
        slug = self.cleaned_data.get('slug')
        if not slug:
            slug = slugify(self.cleaned_data.get('name', ''))
        
        queryset = Tag.objects.filter(slug=slug)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise forms.ValidationError('A tag with this slug already exists.')
        
        return slug