from django.urls import path
from .views import DashboardStatsAPI

urlpatterns = [
    path('stats/', DashboardStatsAPI.as_view(), name='dashboard-stats'),
]