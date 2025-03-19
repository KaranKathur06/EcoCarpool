from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import CustomUser
from rides.models import Ride
from bookings.models import Booking
from payments.models import Payment

class DashboardStatsAPI(APIView):
    def get(self, request):
        try:
            # Total Users (Drivers + Passengers)
            total_users = CustomUser.objects.count()
            
            # Total Rides (Upcoming + Completed)
            total_rides = Ride.objects.count()
            
            # Total Bookings (Confirmed)
            total_bookings = Booking.objects.filter(status='confirmed').count()
            
            # Total Revenue (Completed Payments)
            total_revenue = Payment.objects.filter(status='completed').aggregate(total=Sum('amount'))['total'] or 0
            
            # Recent Rides (Last 5)
            recent_rides = Ride.objects.order_by('-ride_date')[:5].values(
                'id', 'start_location__address', 'end_location__address', 'ride_date'
            )
            
            return Response({
                'total_users': total_users,
                'total_rides': total_rides,
                'total_bookings': total_bookings,
                'total_revenue': total_revenue,
                'recent_rides': recent_rides,
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)