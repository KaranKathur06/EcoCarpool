# rides/views.py
from django.views.generic import ListView
from .models import Ride

class RideListView(ListView):
    model = Ride
    template_name = 'rides/ride_list.html'
    context_object_name = 'rides'

    def get_queryset(self):
        return Ride.objects.filter(ride_date__gte=timezone.now())