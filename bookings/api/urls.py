from django.urls import path , include
from .views import BookingListCreateView, BookingDetailView

urlpatterns = [
    path('', BookingListCreateView.as_view(), name='booking-list'),
    path('<int:pk>/', BookingDetailView.as_view(), name='booking-detail'),
    path('api/', include('bookings.api.urls')),
]