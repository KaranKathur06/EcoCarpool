from rest_framework import generics
from ..models import Ride
from .serializers import RideSerializer

class RideListCreateView(generics.ListCreateAPIView):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer

class RideDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ride.objects.all()
    serializer_class = RideSerializer