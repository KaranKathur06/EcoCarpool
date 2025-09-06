from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard, name='dashboard-home'),
    path('admin/users/', views.AdminUserManagementView.as_view(), name='admin-users'),
    path('admin/rides/', views.AdminRideManagementView.as_view(), name='admin-rides'),
    path('admin/users/<int:user_id>/verify-driver/', views.admin_verify_driver, name='verify-driver'),
    path('admin/users/<int:user_id>/toggle-status/', views.admin_toggle_user_status, name='toggle-user-status'),
    path('admin/rides/<int:ride_id>/action/', views.admin_ride_action, name='ride-action'),
    path('stats/', views.dashboard_stats, name='dashboard-stats'),
    path('chart-data/', views.chart_data, name='chart-data'),
    path('payment-history/', views.payment_history, name='payment-history'),
    path('search-rides/', views.search_rides, name='search-rides'),
]
