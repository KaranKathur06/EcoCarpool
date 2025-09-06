from django.shortcuts import render
from django.db.models import Sum, Count, Avg, Q, F
from datetime import date, datetime
from rides.models import Ride, Booking
from payments.models import Payment, UserPayment, UserRideTip, RidePayout, Transaction
from users.models import CustomUser
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from vehicles.models import Vehicle, VehicleDocument
from django.db.models.functions import TruncMonth, TruncDay, TruncDate
from django.db.models import ExpressionWrapper, FloatField
import json
from django.contrib.auth import get_user_model
from .models import Users, UserRideBook
from django.http import JsonResponse
from reviews.models import Review
from django.contrib.auth.mixins import UserPassesTestMixin
from django.views.generic import ListView
from django.db.models.functions import ExtractWeek, ExtractMonth, ExtractYear

User = get_user_model()

@login_required
def dashboard(request):
    user = request.user
    context = {}

    if user.role == 'admin':
        # Get time ranges
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)

        # User statistics
        total_users = CustomUser.objects.count()
        new_users_today = CustomUser.objects.filter(date_joined__date=today).count()
        drivers_count = CustomUser.objects.filter(role='driver').count()
        passengers_count = CustomUser.objects.filter(role='passenger').count()

        # Ride statistics
        total_rides = Ride.objects.count()
        active_rides = Ride.objects.filter(status='active').count()
        completed_rides = Ride.objects.filter(status='completed').count()
        upcoming_rides = Ride.objects.filter(status='upcoming').count()
        cancelled_rides = Ride.objects.filter(status='cancelled').count()

        # Earnings statistics
        completed_bookings = Booking.objects.filter(status='completed')
        total_platform_earnings = sum(booking.get_total_price() for booking in completed_bookings)
        today_earnings = sum(booking.get_total_price() for booking in completed_bookings.filter(updated_at__date=today))

        # Rating statistics
        platform_rating = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0
        total_reviews = Review.objects.count()

        # User Growth data for the past week
        user_growth_data = []
        for i in range(7):
            date = today - timedelta(days=i)
            count = CustomUser.objects.filter(date_joined__date=date).count()
            user_growth_data.append({
                'date': date.strftime('%a'),
                'count': count
            })
        user_growth_data.reverse()

        # Revenue data for the past week
        revenue_data = []
        for i in range(7):
            date = today - timedelta(days=i)
            day_bookings = completed_bookings.filter(updated_at__date=date)
            revenue_data.append({
                'date': date.strftime('%a'),
                'total': sum(booking.get_total_price() for booking in day_bookings)
            })
        revenue_data.reverse()

        context.update({
            'total_users': total_users,
            'new_users_today': new_users_today,
            'total_platform_earnings': total_platform_earnings,
            'today_earnings': today_earnings,
            'active_rides': active_rides,
            'upcoming_rides': upcoming_rides,
            'platform_rating': round(platform_rating, 1),
            'total_reviews': total_reviews,
            'completed_rides': completed_rides,
            'cancelled_rides': cancelled_rides,
            'drivers_count': drivers_count,
            'passengers_count': passengers_count,
            'user_growth_data': json.dumps(user_growth_data),
            'revenue_data': json.dumps(revenue_data)
        })

    elif user.role == 'driver':
        # Stats cards
        total_rides = user.get_total_rides()
        total_earnings = user.get_total_earnings()
        rating = round(user.get_rating() or 0, 2)
        total_ratings = user.reviews_received.count()
        # CO2 saved: assume 2.3kg per completed ride
        co2_saved = user.driver_rides.filter(status='completed').count() * 2.3

        # Earnings chart (weekly/monthly/yearly)
        now = timezone.now()
        chart_periods = {
            'week': 7,
            'month': 30,
            'year': 365
        }
        earnings_chart = {}
        for period, days in chart_periods.items():
            start_date = now - timedelta(days=days)
            earnings = (
                Payment.objects.filter(receiver=user, status='completed', created_at__gte=start_date)
                .annotate(day=TruncDate('created_at'))
                .values('day')
                .annotate(total=Sum('amount'))
                .order_by('day')
            )
            labels = []
            data = []
            for i in range(days):
                day = (start_date + timedelta(days=i)).date()
                labels.append(day.strftime('%b %d'))
                found = next((e['total'] for e in earnings if e['day'] == day), 0)
                data.append(float(found) if found else 0)
            earnings_chart[period] = {'labels': labels, 'data': data}

        # Upcoming rides (next 5)
        upcoming_rides = Ride.objects.filter(driver=user, ride_date__gte=now, status__in=['active', 'pending']).order_by('ride_date')[:5]

        # Vehicle status (first vehicle)
        vehicle = Vehicle.objects.filter(owner=user).first()
        vehicle_status = None
        if vehicle:
            vehicle_status = {
                'brand': str(vehicle.company),
                'model': str(vehicle.model),
                'license_plate': vehicle.license_plate,
                'fuel_type': vehicle.get_fuel_type_display(),
                'seating_capacity': vehicle.seating_capacity,
                'year': vehicle.year,
                'color': vehicle.color,
                'is_active': vehicle.is_active,
                'photo': vehicle.vehicle_photo.url if vehicle.vehicle_photo else None,
                'mileage': vehicle.mileage,
            }

        # Ride distribution (pie chart: by type or time of day, here by status)
        ride_status_counts = user.driver_rides.values('status').annotate(count=Count('id'))
        ride_distribution = {item['status']: item['count'] for item in ride_status_counts}

        # Recent reviews (last 3)
        recent_reviews = Review.objects.filter(reviewed=user).order_by('-created_at')[:3]
        
        # Popular routes (top 3 by count, with coordinates if available)
        popular_routes = (
            user.driver_rides.values('start_location', 'end_location')
            .annotate(count=Count('id'))
            .order_by('-count')[:3]
        )
        # For map: get coordinates if possible (not implemented here, placeholder)
        for route in popular_routes:
            route['start_lat'] = None
            route['start_lng'] = None
            route['end_lat'] = None
            route['end_lng'] = None

        # Recent activity (last 5 completed/cancelled rides)
        recent_activity = (
            Ride.objects.filter(driver=user, status__in=['completed', 'cancelled'])
            .order_by('-ride_date')[:5]
        )
        
        context.update({
            'total_rides': total_rides,
            'total_earnings': total_earnings,
            'rating': rating,
            'total_ratings': total_ratings,
            'co2_saved': co2_saved,
            'earnings_chart': earnings_chart,
            'earnings_chart_json': json.dumps(earnings_chart['month']),
            'upcoming_rides': upcoming_rides,
            'vehicle_status': vehicle_status,
            'ride_distribution': ride_distribution,
            'ride_distribution_json': json.dumps(ride_distribution),
            'recent_reviews': recent_reviews,
            'popular_routes': popular_routes,
            'recent_activity': recent_activity,
        })

    else:
        # Passenger statistics
        total_trips = user.bookings.count()
        week_trips = user.bookings.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Get recent bookings
        recent_bookings = user.bookings.order_by('-created_at')[:5]
        
        # Get favorite routes
        favorite_routes = user.get_favorite_routes_count()
        
        context.update({
            'total_trips': total_trips,
            'week_trips': week_trips,
            'money_saved': user.get_total_savings(),
            'co2_reduced': user.get_co2_reduction(),
            'favorite_routes': favorite_routes,
            'recent_bookings': recent_bookings
        })

    return render(request, 'dashboard/dashboard.html', context)

@login_required
def dashboard_stats(request):
    stat_type = request.GET.get('type')
    user = request.user
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)

    if stat_type == 'users':
        current = CustomUser.objects.count()
        previous = CustomUser.objects.filter(date_joined__lt=month_ago).count()
        change = ((current - previous) / previous * 100) if previous > 0 else 0
        return JsonResponse({
            'value': current,
            'change': change,
            'change_text': f'{abs(round(change, 1))}% from last month'
        })

    elif stat_type == 'rides':
        current = Ride.objects.count()
        previous = Ride.objects.filter(created_at__lt=week_ago).count()
        change = ((current - previous) / previous * 100) if previous > 0 else 0
        return JsonResponse({
            'value': current,
            'change': change,
            'change_text': f'{abs(round(change, 1))}% from last week'
        })

    elif stat_type == 'earnings':
        current = sum(booking.get_total_price() for booking in Booking.objects.filter(status='completed'))
        previous = sum(booking.get_total_price() for booking in Booking.objects.filter(status='completed', updated_at__lt=month_ago))
        change = ((current - previous) / previous * 100) if previous > 0 else 0
        return JsonResponse({
            'value': f'${current:.2f}',
            'change': change,
            'change_text': f'{abs(round(change, 1))}% from last month'
        })

    elif stat_type == 'transactions':
        current = Transaction.objects.count()
        previous = Transaction.objects.filter(created_at__lt=month_ago).count()
        change = ((current - previous) / previous * 100) if previous > 0 else 0
        return JsonResponse({
            'value': f'${current:.2f}',
            'change': change,
            'change_text': f'{abs(round(change, 1))}% from last month'
        })

    elif stat_type == 'passengers':
        current = Booking.objects.filter(status='completed').count()
        today_count = Booking.objects.filter(status='completed', created_at__date=today).count()
        return JsonResponse({
            'value': current,
            'change': 0,
            'change_text': f'Today: {today_count}'
        })

    elif stat_type == 'your-rides':
        current = Ride.objects.filter(driver=user).count()
        upcoming = Ride.objects.filter(driver=user, status='upcoming').count()
        return JsonResponse({
            'value': current,
            'change': 0,
            'change_text': f'Upcoming: {upcoming}'
        })

    elif stat_type == 'your-earnings':
        current = user.get_total_earnings()
        today_earnings = user.get_today_earnings()
        return JsonResponse({
            'value': f'${current:.2f}',
            'change': 0,
            'change_text': f'Today: ${today_earnings:.2f}'
        })

    return JsonResponse({'error': 'Invalid stat type'}, status=400)

@login_required
def chart_data(request):
    chart_type = request.GET.get('chart')
    period = request.GET.get('period', 'week')
    user = request.user
    
    now = timezone.now()
    
    if period == 'week':
        start_date = now - timedelta(days=7)
        date_format = '%b %d'
    elif period == 'month':
        start_date = now - timedelta(days=30)
        date_format = '%b %d'
    else:  # year
        start_date = now - timedelta(days=365)
        date_format = '%b'
    
    data = {
        'labels': [],
        'datasets': []
    }
    
    current = start_date.date()
    dates = []
    while current <= now.date():
        dates.append(current)
        data['labels'].append(current.strftime(date_format))
        current += timedelta(days=1)
    
    if user.role == 'driver':
        if chart_type == 'earningsChart':
            earnings_data = (Payment.objects
                .filter(receiver=user, status='completed', created_at__gte=start_date)
                .annotate(date=TruncDate('created_at'))
                .values('date')
                .annotate(total=Sum('amount'))
                .order_by('date'))
            
            earnings_values = []
            for date in dates:
                daily_earning = next((item['total'] for item in earnings_data if item['date'] == date), 0)
                earnings_values.append(daily_earning)
            
            data['datasets'].append({
                'label': 'Earnings',
                'data': earnings_values,
                'borderColor': '#4169E1',
                'backgroundColor': 'rgba(65, 105, 225, 0.1)',
                'fill': True
            })
        
        elif chart_type == 'ridesChart':
            ride_data = (Ride.objects
                .filter(driver=user, ride_date__gte=start_date)
                .annotate(date=TruncDate('ride_date'))
                .values('date', 'status')
                .annotate(count=Count('id'))
                .order_by('date'))
            
            completed_rides = []
            cancelled_rides = []
            
            for date in dates:
                completed = next((item['count'] for item in ride_data if item['date'] == date and item['status'] == 'completed'), 0)
                cancelled = next((item['count'] for item in ride_data if item['date'] == date and item['status'] == 'cancelled'), 0)
                completed_rides.append(completed)
                cancelled_rides.append(cancelled)
            
            data['datasets'].extend([
                {
                    'label': 'Completed Rides',
                    'data': completed_rides,
                    'backgroundColor': '#4169E1',
                    'borderColor': '#4169E1'
                },
                {
                    'label': 'Cancelled Rides',
                    'data': cancelled_rides,
                    'backgroundColor': '#dc3545',
                    'borderColor': '#dc3545'
                }
            ])
    
    else:  # Passenger
        if chart_type == 'tripHistoryChart':
            trip_data = (Booking.objects
                .filter(passenger=user, created_at__gte=start_date)
                .annotate(date=TruncDate('created_at'))
                .values('date')
                .annotate(count=Count('id'))
                .order_by('date'))
            
            trip_values = []
            for date in dates:
                daily_trips = next((item['count'] for item in trip_data if item['date'] == date), 0)
                trip_values.append(daily_trips)
            
            data['datasets'].append({
                'label': 'Trips',
                'data': trip_values,
                'borderColor': '#4169E1',
                'backgroundColor': 'rgba(65, 105, 225, 0.1)',
                'fill': True
            })
    
    return JsonResponse(data)

@login_required
def payment_history(request):
    user = request.user
    
    # Get user's payments
    payments_made = Payment.objects.filter(payer=user).order_by('-created_at')
    payments_received = Payment.objects.filter(receiver=user).order_by('-created_at')

    context = {
        'payments_made': payments_made,
        'payments_received': payments_received,
    }
    
    return render(request, 'dashboard/payment_history.html', context)

@login_required
def search_rides(request):
    """View for searching available rides"""
    context = {}
    
    # Get search parameters
    start_location = request.GET.get('start_location')
    end_location = request.GET.get('end_location')
    date = request.GET.get('date')
    
    # Base query for available rides
    rides = Ride.objects.filter(
        status='available',
        available_seats__gt=0
    )
    
    # Apply filters if provided
    if start_location:
        rides = rides.filter(start_location__icontains=start_location)
    if end_location:
        rides = rides.filter(end_location__icontains=end_location)
    if date:
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            rides = rides.filter(
                ride_date__date=date_obj
            )
        except ValueError:
            pass
    
    # Order by date and time
    rides = rides.order_by('ride_date')
    
    context['rides'] = rides
    context['search_params'] = {
        'start_location': start_location,
        'end_location': end_location,
        'date': date
    }
    
    return render(request, 'dashboard/search_rides.html', context)

class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'admin'

class AdminUserManagementView(AdminRequiredMixin, ListView):
    model = CustomUser
    template_name = 'dashboard/admin/user_management.html'
    context_object_name = 'users'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        role_filter = self.request.GET.get('role')
        status_filter = self.request.GET.get('status')
        
        users = CustomUser.objects.all()
        
        if query:
            users = users.filter(
                Q(username__icontains=query) |
                Q(email__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            )
        
        if role_filter:
            users = users.filter(role=role_filter)
            
        if status_filter:
            users = users.filter(is_active=(status_filter == 'active'))
            
        return users.order_by('-date_joined')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_users'] = CustomUser.objects.count()
        context['active_users'] = CustomUser.objects.filter(is_active=True).count()
        context['drivers'] = CustomUser.objects.filter(role='driver').count()
        context['passengers'] = CustomUser.objects.filter(role='passenger').count()
        return context

class AdminRideManagementView(AdminRequiredMixin, ListView):
    model = Ride
    template_name = 'dashboard/admin/ride_management.html'
    context_object_name = 'rides'
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get('q')
        status_filter = self.request.GET.get('status')
        date_filter = self.request.GET.get('date')
        
        rides = Ride.objects.all()
        
        if query:
            rides = rides.filter(
                Q(driver__username__icontains=query) |
                Q(start_location__icontains=query) |
                Q(end_location__icontains=query)
            )
        
        if status_filter:
            rides = rides.filter(status=status_filter)
            
        if date_filter:
            if date_filter == 'today':
                rides = rides.filter(ride_date__date=timezone.now().date())
            elif date_filter == 'week':
                rides = rides.filter(ride_date__gte=timezone.now() - timedelta(days=7))
            elif date_filter == 'month':
                rides = rides.filter(ride_date__gte=timezone.now() - timedelta(days=30))
                
        return rides.order_by('-ride_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_rides'] = Ride.objects.count()
        context['active_rides'] = Ride.objects.filter(status='active').count()
        context['completed_rides'] = Ride.objects.filter(status='completed').count()
        context['cancelled_rides'] = Ride.objects.filter(status='cancelled').count()
        
        # Calculate average ratings
        context['avg_ride_rating'] = Review.objects.aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Popular routes
        context['popular_routes'] = Ride.objects.values('start_location', 'end_location')\
            .annotate(count=Count('id'))\
            .order_by('-count')[:5]
            
        return context

@login_required
def admin_verify_driver(request, user_id):
    if not request.user.role == 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    try:
        driver = CustomUser.objects.get(id=user_id, role='driver')
        driver.is_verified = True
        driver.save()
        return JsonResponse({'message': 'Driver verified successfully'})
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Driver not found'}, status=404)

@login_required
def admin_toggle_user_status(request, user_id):
    if not request.user.role == 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    try:
        user = CustomUser.objects.get(id=user_id)
        user.is_active = not user.is_active
        user.save()
        return JsonResponse({
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully',
            'is_active': user.is_active
        })
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)

@login_required
def admin_ride_action(request, ride_id):
    if not request.user.role == 'admin':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    try:
        ride = Ride.objects.get(id=ride_id)
        action = request.POST.get('action')
        
        if action == 'cancel':
            ride.status = 'cancelled'
            # Notify users affected by cancellation
            # Send notifications to driver and passengers
        elif action == 'complete':
            ride.status = 'completed'
        
        ride.save()
        return JsonResponse({'message': f'Ride {action}ed successfully'})
    except Ride.DoesNotExist:
        return JsonResponse({'error': 'Ride not found'}, status=404)