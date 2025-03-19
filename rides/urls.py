from django.urls import path
from . import views

app_name = 'rides'
urlpatterns = [
    path('', views.RideListView.as_view(), name='rides'), 
    path('<int:pk>/', views.RideDetailView.as_view(), name='ride-detail'),
]