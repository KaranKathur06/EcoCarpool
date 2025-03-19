from django.urls import path
from .views import RideListCreateView, RideDetailView

urlpatterns = [
    path('', RideListCreateView.as_view(), name='ride-list'),
    path('<int:pk>/', RideDetailView.as_view(), name='ride-detail'),
]