from django.urls import path
from . import views

app_name = 'vehicles'
urlpatterns = [
    path('', views.VehicleListView.as_view(), name='vehicles'), 
    path('add/', views.VehicleCreateView.as_view(), name='add-vehicle'),
]