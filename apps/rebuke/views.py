"""
Rebuke is a themed section of the site, not a separate content model.

Posts are created exactly like any other post (Django admin, or wherever
posts get created elsewhere in the CMS) and images are uploaded exactly
like any other post's featured image, via the Media Library. What makes a
post show up here is simply belonging to the Category with slug "rebuke".

This keeps a single source of truth for content (apps.posts.Post) and for
uploads (apps.media_library.Media) instead of duplicating that machinery,
while still giving "Rebuke" its own URL space and its own template styling
(templates/rebuke/index.html, templates/rebuke/detail.html).
"""
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView

from apps.posts.models import Post, Category

REBUKE_CATEGORY_SLUG = 'rebuke'


class RebukeListView(ListView):
    """List all published posts in the Rebuke category."""

    model = Post
    template_name = 'rebuke/index.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return Post.published().filter(
            category__slug=REBUKE_CATEGORY_SLUG
        ).select_related('category', 'author', 'featured_image').prefetch_related('tags')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['nav_categories'] = Category.objects.all()
        return context


class RebukeDetailView(DetailView):
    """Display a single published post in the Rebuke category."""

    model = Post
    template_name = 'rebuke/detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Post.published().filter(
            category__slug=REBUKE_CATEGORY_SLUG
        ).select_related('category', 'author', 'featured_image').prefetch_related('tags')

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        obj.increment_view_count()
        return obj

    def get_context_data(self, **kwargs):
        """Previous/next navigation scoped to the Rebuke category only,
        since Post.get_next_post()/get_previous_post() look across all
        categories and would otherwise link to a post outside this
        section's URL space."""
        context = super().get_context_data(**kwargs)
        post = self.object
        rebuke_posts = Post.published().filter(category__slug=REBUKE_CATEGORY_SLUG)
        context['prev_post'] = rebuke_posts.filter(
            published_at__lt=post.published_at
        ).order_by('-published_at').first()
        context['next_post'] = rebuke_posts.filter(
            published_at__gt=post.published_at
        ).order_by('published_at').first()
        return context
