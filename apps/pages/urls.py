from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    # Contact page - specific route
    path('contact/', views.ContactView.as_view(), name='contact'),

    # List of all published pages
    path('list/', views.PageListView.as_view(), name='list'),

    # Preview any page regardless of status (admin only)
    path('preview/<slug:slug>/', views.PagePreviewView.as_view(), name='preview'),
    
    # About page
    path('about/', views.PageDetailView.as_view(), {'slug': 'about'}, name='about'),
    
    # Page detail view - catch all pages
    path('<slug:slug>/', views.PageDetailView.as_view(), name='detail'),
]

# For REST API:
# from rest_framework.routers import DefaultRouter
# from .views import PageViewSet
# router = DefaultRouter()
# router.register('api/pages', PageViewSet, basename='page-api')
# urlpatterns += router.urls