from django.views.generic import ListView, DetailView
from .models import Ride

class RideListView(ListView):
    model = Ride
    template_name = 'rides/ride_list.html'
    context_object_name = 'rides'

class RideDetailView(DetailView):
    model = Ride
    template_name = 'rides/ride_detail.html'