from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [
    path('', views.vehicle_list, name='vehicle-list'),
    path('add/', views.add_vehicle, name='add_vehicle'),
    path('edit/<int:pk>/', views.edit_vehicle, name='edit_vehicle'),
    path('<int:pk>/', views.VehicleDetailView.as_view(), name='vehicle-detail'),
    path('<int:pk>/update/', views.VehicleUpdateView.as_view(), name='vehicle-update'),
    path('<int:pk>/delete/', views.VehicleDeleteView.as_view(), name='vehicle-delete'),
    path('<int:vehicle_pk>/add-document/', views.add_document, name='add-document'),
    path('document/<int:pk>/delete/', views.delete_document, name='delete-document'),
    path('api/companies/', views.get_companies_by_type, name='api_companies'),
    path('api/models/', views.get_models_by_company, name='api_models'),
]