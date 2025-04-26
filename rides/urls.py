from django.urls import path
from . import views

app_name = 'rides'

urlpatterns = [
    path('', views.RideListView.as_view(), name='ride-list'),
    path('create/', views.RideCreateView.as_view(), name='ride-create'),
    path('<int:pk>/', views.RideDetailView.as_view(), name='ride-detail'),
    path('<int:pk>/update/', views.RideUpdateView.as_view(), name='ride-update'),
    path('<int:pk>/delete/', views.RideDeleteView.as_view(), name='ride-delete'),
    path('search/', views.search_rides, name='ride-search'),
    path('my-rides/', views.RideListView.as_view(), name='my-rides'),
    path('bookings/', views.BookingListView.as_view(), name='bookings'),
    path('api/vehicles/', views.get_user_vehicles, name='user-vehicles'),
    path('my-bookings/', views.my_bookings, name='my-bookings'),
    path('<int:ride_id>/book/', views.book_ride, name='book-ride'),
    path('booking/<int:pk>/cancel/', views.cancel_booking, name='cancel-booking'),
    path('all-rides/', views.AllRidesView.as_view(), name='all-rides'),
]