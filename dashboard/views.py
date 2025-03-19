from django.shortcuts import render
from django.db.models import Sum, Count
from datetime import date
from rides.models import Ride
from bookings.models import Booking  
from payments.models import Payment  
from users.models import CustomUser
from django.utils import timezone

def dashboard_home(request):
    # Users Statistics
    total_users = CustomUser.objects.count()
    
    # Rides Statistics
    total_rides = Ride.objects.count()
    
    # For today's rides
    today_rides = Ride.objects.filter(
        ride_date__date=timezone.now().date()  
    ).count()
    
    # For monthly rides
    month_rides = Ride.objects.filter(
        ride_date__month=timezone.now().month,  
        ride_date__year=timezone.now().year     
    ).count()
    
    # Today's Earnings
    today_earnings = Payment.objects.filter(
        booking__ride__ride_date__date=date.today(),
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Total Earnings
    total_earnings = Payment.objects.filter(
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Expenses (Example calculation - adjust according to your models)
    total_expenses = 0

    context = {
        'total_users': total_users,
        'total_rides': total_rides,
        'today_rides': today_rides,
        'month_rides': month_rides,
        'today_earnings': today_earnings,
        'total_earnings': total_earnings,
        'total_expenses': total_expenses,
    }
    return render(request, 'dashboard/home.html', context)