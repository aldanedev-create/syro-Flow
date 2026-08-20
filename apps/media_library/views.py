from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

from django.db import models
from .models import Media, MediaCategory
from .forms import MediaUploadForm


class GalleryView(ListView):
    """Display gallery of uploaded media"""
    
    model = Media
    template_name = 'gallery/index.html'
    context_object_name = 'media_items'
    paginate_by = 24  # Grid layout, multiples of 4, 6, 8
    
    def get_queryset(self):
        """Get all media ordered by newest"""
        return Media.objects.all().select_related(
            'uploaded_by'
        ).prefetch_related('categories').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Gallery'
        context['categories'] = MediaCategory.objects.annotate(
            media_count=models.Count('media')
        ).filter(media_count__gt=0)
        return context


class GalleryCategoryView(ListView):
    """Display media in a specific category"""
    
    model = Media
    template_name = 'gallery/category.html'
    context_object_name = 'media_items'
    paginate_by = 24
    
    def get_queryset(self):
        """Get media in the category"""
        self.category = get_object_or_404(MediaCategory, slug=self.kwargs['slug'])
        return Media.objects.filter(
            categories=self.category
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['page_title'] = f'Gallery: {self.category.name}'
        return context


class MediaDetailView(DetailView):
    """Display a single media item"""
    
    model = Media
    template_name = 'gallery/image_detail.html'
    context_object_name = 'media_item'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        media_item = self.get_object()
        
        # Get related media (same category)
        categories = media_item.categories.all()
        related_media = Media.objects.filter(
            categories__in=categories
        ).exclude(id=media_item.id).distinct()[:8]
        
        context['related_media'] = related_media
        context['page_title'] = media_item.title
        context['page_description'] = media_item.caption or media_item.description
        
        return context


class MediaUploadView(LoginRequiredMixin, View):
    """Handle media file uploads (AJAX)"""
    
    def post(self, request, *args, **kwargs):
        """Process uploaded file"""
        form = MediaUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            media = form.save(commit=False)
            media.uploaded_by = request.user
            media.save()
            
            # Add categories if provided
            if form.cleaned_data.get('categories'):
                media.categories.set(form.cleaned_data['categories'])
            
            return JsonResponse({
                'success': True,
                'id': media.id,
                'title': media.title,
                'url': media.get_absolute_url(),
                'thumbnail': media.get_thumbnail_url(),
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors,
            }, status=400)
    
    def get(self, request, *args, **kwargs):
        """Render upload form (optional)"""
        form = MediaUploadForm()
        context = {
            'form': form,
            'categories': MediaCategory.objects.all(),
        }
        return render(request, 'gallery/upload.html', context)


class MediaDeleteView(LoginRequiredMixin, View):
    """Delete a media item (admin only)"""
    
    def post(self, request, *args, **kwargs):
        """Delete the specified media item"""
        if not request.user.is_staff:
            return JsonResponse({
                'success': False,
                'error': 'Permission denied'
            }, status=403)
        
        pk = self.kwargs.get('pk')
        media = get_object_or_404(Media, pk=pk)
        
        # Check if media is used in posts
        if media.posts.exists():
            return JsonResponse({
                'success': False,
                'error': 'Cannot delete media that is used in posts'
            }, status=400)
        
        # Delete the file and record
        media.file.delete()
        media.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Media deleted successfully'
        })