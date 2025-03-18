# bookings/views.py
from django.views.generic import ListView, DetailView
from .models import Booking  # Make sure this matches your model

class BookingListView(ListView):
    model = Booking
    template_name = 'bookings/booking_list.html'
    context_object_name = 'bookings'  # Should match template variable

class BookingDetailView(DetailView):
    model = Booking
    template_name = 'bookings/booking_detail.html'