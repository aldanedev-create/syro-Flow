from django.urls import path
from . import views

app_name = 'media_library'

urlpatterns = [
    # Gallery
    path('', views.GalleryView.as_view(), name='gallery'),
    path('<int:pk>/', views.MediaDetailView.as_view(), name='detail'),
    
    # Category views
    path('category/<slug:slug>/', views.GalleryCategoryView.as_view(), name='category'),
    
    # Upload (AJAX)
    path('upload/', views.MediaUploadView.as_view(), name='upload'),

    # Delete (AJAX)
    path('<int:pk>/delete/', views.MediaDeleteView.as_view(), name='delete_media'),
    
    # API endpoints (if using DRF)
    # path('api/media/', views.MediaAPIView.as_view(), name='api-list'),
    # path('api/media/<int:pk>/', views.MediaAPIDetailView.as_view(), name='api-detail'),
]

# For REST API:
# from rest_framework.routers import DefaultRouter
# from .views import MediaViewSet
# router = DefaultRouter()
# router.register('api/media', MediaViewSet, basename='media-api')
# urlpatterns += router.urls