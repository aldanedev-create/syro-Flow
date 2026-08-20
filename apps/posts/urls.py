from django.urls import path
from . import views

app_name = 'posts'

urlpatterns = [
    # Post listing
    path('', views.PostListView.as_view(), name='list'),

    # Category views
    path('category/<slug:slug>/', views.CategoryView.as_view(), name='category'),

    # Tag views
    path('tag/<slug:slug>/', views.TagView.as_view(), name='tag'),

    # Search
    path('search/', views.SearchView.as_view(), name='search'),

    # Archive by year/month
    path('archive/<int:year>/', views.ArchiveView.as_view(), name='archive_year'),
    path('archive/<int:year>/<int:month>/', views.ArchiveView.as_view(), name='archive_month'),

    # Post detail - catch-all slug route must stay last so it doesn't
    # shadow the literal routes above (category/, tag/, search/, archive/).
    path('<slug:slug>/', views.PostDetailView.as_view(), name='detail'),

    # RSS Feed (optional)
    # path('feed/', views.PostFeed(), name='feed'),
]

# Uncomment for REST API endpoints
# from rest_framework.routers import DefaultRouter
# from .views import PostViewSet
# router = DefaultRouter()
# router.register('api/posts', PostViewSet, basename='post-api')
# urlpatterns += router.urls