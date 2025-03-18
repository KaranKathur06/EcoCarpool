from django.shortcuts import render
from django.db.models import Sum, Count
from datetime import date
from rides.models import Ride
from bookings.models import Booking,Payment
from users.models import User   
from django.utils import timezone

def dashboard_home(request):
    # Users Statistics
    total_users = User.objects.count()
    
    # Rides Statistics
    total_rides = Ride.objects.count()
    # For today's rides
    today_rides = Ride.objects.filter(
        start_time__date=timezone.now().date()
    ).count()

    # For monthly rides
    month_rides = Ride.objects.filter(
        start_time__month=timezone.now().month,
        start_time__year=timezone.now().year
    ).count()
    
    # Today's Earnings
    today_earnings = Payment.objects.filter(
        booking__ride__start_time__date=date.today(),
        transaction_status='success'
    ).aggregate(total=Sum('amount'))['total'] or 0

    # Total Earnings
    total_earnings = Payment.objects.filter(
        transaction_status='success'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Expenses (Example calculation - adjust according to your models)
    total_promocodes = Booking.objects.aggregate(total=Sum('promocode__discount'))['total'] or 0
    transaction_charges = total_earnings * 0.02  # Assuming 2% transaction charges
    total_expenses = total_promocodes + transaction_charges

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