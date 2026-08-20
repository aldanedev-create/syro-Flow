from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils.timezone import now
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views import View

from .models import Post, Category, Tag
from .forms import PostSearchForm


class PostListView(ListView):
    """List all published posts with pagination"""
    
    model = Post
    template_name = 'posts/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        """Get published posts ordered by most recent"""
        return Post.published().select_related(
            'category', 'author', 'featured_image'
        ).prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'All Posts'
        context['page_description'] = 'Browse all articles and teachings'
        return context


class PostDetailView(DetailView):
    """Display a single published post"""
    
    model = Post
    template_name = 'posts/post_detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'
    
    def get_queryset(self):
        """Get published posts only"""
        return Post.published().select_related(
            'category', 'author', 'featured_image'
        ).prefetch_related('tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        
        # Increment view count
        post.increment_view_count()
        
        # Get related posts (same category)
        related_posts = Post.published().filter(
            category=post.category
        ).exclude(id=post.id)[:4]
        
        context['related_posts'] = related_posts
        context['page_title'] = post.title
        context['page_description'] = post.excerpt or post.seo_description
        
        return context


class CategoryView(ListView):
    """Display posts in a specific category"""
    
    model = Post
    template_name = 'posts/category.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        """Get published posts in the category"""
        self.category = get_object_or_404(Category, slug=self.kwargs['slug'])
        return Post.published().filter(
            category=self.category
        ).select_related('author', 'featured_image')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['page_title'] = f'Category: {self.category.name}'
        context['page_description'] = self.category.description
        return context


class TagView(ListView):
    """Display posts with a specific tag"""
    
    model = Post
    template_name = 'posts/tag.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        """Get published posts with the tag"""
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return Post.published().filter(
            tags=self.tag
        ).select_related('author', 'featured_image')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        context['page_title'] = f'Tag: {self.tag.name}'
        return context


class SearchView(ListView):
    """Search posts by title, content, or excerpt"""
    
    model = Post
    template_name = 'posts/search.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        """Search published posts"""
        query = self.request.GET.get('q', '').strip()
        self.query = query
        
        if not query:
            return Post.published().none()
        
        return Post.published().filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query)
        ).distinct().select_related('author', 'featured_image')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.query
        context['page_title'] = f'Search: {self.query}' if self.query else 'Search'
        return context


class ArchiveView(ListView):
    """Display posts by year/month archive"""
    
    model = Post
    template_name = 'posts/archive.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        """Filter posts by year and optionally month"""
        year = self.kwargs['year']
        month = self.kwargs.get('month')
        
        self.year = year
        self.month = month
        
        queryset = Post.published().filter(
            published_at__year=year
        ).select_related('author', 'featured_image')
        
        if month:
            queryset = queryset.filter(published_at__month=month)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['year'] = self.year
        context['month'] = self.month
        context['page_title'] = f'Archive: {self.year}' + (f'/{self.month}' if self.month else '')
        return context