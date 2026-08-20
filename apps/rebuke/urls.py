from django.urls import path
from . import views

app_name = 'rebuke'

urlpatterns = [
    path('', views.RebukeListView.as_view(), name='index'),
    path('<slug:slug>/', views.RebukeDetailView.as_view(), name='detail'),
]
