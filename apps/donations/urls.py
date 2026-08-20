from django.urls import path
from . import views

app_name = 'donations'

urlpatterns = [
    # Main donation page
    path('', views.DonationView.as_view(), name='index'),
    
    # Donation form / processing
    path('donate/', views.DonationCreateView.as_view(), name='donate'),
    path('thank-you/', views.DonationThankYouView.as_view(), name='thank_you'),
    
    # Transaction status
    path('transaction/<str:transaction_id>/', views.TransactionStatusView.as_view(), name='transaction_status'),
    
    # Goals
    path('goals/', views.GoalListView.as_view(), name='goals'),
    path('goals/<int:pk>/', views.GoalDetailView.as_view(), name='goal_detail'),
]

# For REST API:
# from rest_framework.routers import DefaultRouter
# from .views import DonationViewSet, GoalViewSet
# router = DefaultRouter()
# router.register('api/donations', DonationViewSet, basename='donation-api')
# router.register('api/goals', GoalViewSet, basename='goal-api')
# urlpatterns += router.urls
