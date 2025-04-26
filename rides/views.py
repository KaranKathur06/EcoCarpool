# rides/views.py
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.utils import timezone
from .models import Ride, Location, Booking
from vehicles.models import Vehicle
from .forms import RideSearchForm, RideForm, BookingForm
from users.models import CustomUser
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

class RideListView(LoginRequiredMixin, ListView):
    model = Ride
    template_name = 'rides/ride_list.html'
    context_object_name = 'rides'
    paginate_by = 10

    def get_queryset(self):
        return Ride.objects.filter(
            Q(driver=self.request.user) | 
            Q(bookings__passenger=self.request.user)
        ).distinct().order_by('-ride_date')

class RideDetailView(LoginRequiredMixin, DetailView):
    model = Ride
    template_name = 'rides/ride_detail.html'
    context_object_name = 'ride'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ride = self.get_object()
        context['can_book'] = ride.can_book()
        context['available_seats'] = ride.get_available_seats_count()
        return context

class RideCreateView(LoginRequiredMixin, CreateView):
    model = Ride
    form_class = RideForm
    template_name = 'rides/ride_form.html'
    success_url = reverse_lazy('rides:my-rides')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.driver = self.request.user
        return super().form_valid(form)

class RideUpdateView(LoginRequiredMixin, UpdateView):
    model = Ride
    form_class = RideForm
    template_name = 'rides/ride_form.html'
    success_url = reverse_lazy('rides:my-rides')

    def get_queryset(self):
        return Ride.objects.filter(driver=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

class RideDeleteView(LoginRequiredMixin, DeleteView):
    model = Ride
    template_name = 'rides/ride_confirm_delete.html'
    success_url = reverse_lazy('rides:my-rides')

    def get_queryset(self):
        return Ride.objects.filter(driver=self.request.user)

class RideSearchView(LoginRequiredMixin, ListView):
    model = Ride
    template_name = 'rides/ride_search.html'
    context_object_name = 'rides'
    paginate_by = 10

    def get_queryset(self):
        form = RideSearchForm(self.request.GET)
        if form.is_valid():
            queryset = Ride.objects.filter(status='active')
            
            # Filter by date range
            if form.cleaned_data.get('date_from'):
                queryset = queryset.filter(ride_date__gte=form.cleaned_data['date_from'])
            if form.cleaned_data.get('date_to'):
                queryset = queryset.filter(ride_date__lte=form.cleaned_data['date_to'])

            # Filter by price range
            if form.cleaned_data.get('price_from'):
                queryset = queryset.filter(price_per_seat__gte=form.cleaned_data['price_from'])
            if form.cleaned_data.get('price_to'):
                queryset = queryset.filter(price_per_seat__lte=form.cleaned_data['price_to'])

            # Filter by seats
            if form.cleaned_data.get('seats'):
                queryset = queryset.filter(available_seats__gte=form.cleaned_data['seats'])

            # Filter by location
            if form.cleaned_data.get('start_location'):
                queryset = queryset.filter(start_location__icontains=form.cleaned_data['start_location'])
            if form.cleaned_data.get('end_location'):
                queryset = queryset.filter(end_location__icontains=form.cleaned_data['end_location'])

            return queryset
        return Ride.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = RideSearchForm(self.request.GET)
        return context

from django.http import HttpResponse

def index(request):
    return HttpResponse("Welcome to the rides app!")

def ride_list(request):
    rides = Ride.objects.all()
    return render(request, 'rides/ride_list.html', {'rides': rides})

def ride_detail(request, pk):
    ride = Ride.objects.get(pk=pk)
    return render(request, 'rides/ride_detail.html', {'ride': ride})

class MyRidesView(LoginRequiredMixin, ListView):
    model = Ride
    template_name = 'rides/my_rides.html'
    context_object_name = 'rides'
    paginate_by = 9  # Show 9 rides per page (3x3 grid)
    
    def get_queryset(self):
        queryset = Ride.objects.filter(driver=self.request.user)
        
        # Handle search
        search = self.request.GET.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(start_location__icontains=search) |
                Q(end_location__icontains=search)
            )
        
        # Handle status filter
        status = self.request.GET.get('status', 'all')
        if status != 'all':
            queryset = queryset.filter(status=status)
            
        # Handle date filter
        date_filter = self.request.GET.get('date', 'all')
        today = timezone.now().date()
        if date_filter == 'today':
            queryset = queryset.filter(ride_date__date=today)
        elif date_filter == 'week':
            week_ago = today - timezone.timedelta(days=7)
            queryset = queryset.filter(ride_date__date__gte=week_ago)
        elif date_filter == 'month':
            month_ago = today - timezone.timedelta(days=30)
            queryset = queryset.filter(ride_date__date__gte=month_ago)
            
        # Handle sorting
        sort = self.request.GET.get('sort', 'date_desc')
        if sort == 'date_desc':
            queryset = queryset.order_by('-ride_date')
        elif sort == 'date_asc':
            queryset = queryset.order_by('ride_date')
        elif sort == 'price_high':
            queryset = queryset.order_by('-price_per_seat')
        elif sort == 'price_low':
            queryset = queryset.order_by('price_per_seat')
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add filter states to context
        context.update({
            'search': self.request.GET.get('search', ''),
            'status': self.request.GET.get('status', 'all'),
            'date': self.request.GET.get('date', 'all'),
            'sort': self.request.GET.get('sort', 'date_desc'),
            'total_rides': self.get_queryset().count(),
            'active_rides': self.get_queryset().filter(status='active').count(),
            'completed_rides': self.get_queryset().filter(status='completed').count(),
            'cancelled_rides': self.get_queryset().filter(status='cancelled').count(),
        })
        return context

class MyBookingsView(LoginRequiredMixin, ListView):
    model = Ride
    template_name = 'rides/my_bookings.html'
    context_object_name = 'bookings'
    
    def get_queryset(self):
        return self.request.user.bookings.all().order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_bookings'] = self.get_queryset().filter(status='confirmed')
        context['past_bookings'] = self.get_queryset().filter(status='completed')
        context['cancelled_bookings'] = self.get_queryset().filter(status='cancelled')
        return context

def search_rides(request):
    if request.method == 'GET':
        start_location = request.GET.get('start_location')
        end_location = request.GET.get('end_location')
        date = request.GET.get('date')

        rides = Ride.objects.filter(status='pending')

        if start_location:
            rides = rides.filter(start_location__icontains=start_location)
        if end_location:
            rides = rides.filter(end_location__icontains=end_location)
        if date:
            rides = rides.filter(ride_date__date=date)

        context = {
            'rides': rides,
            'start_location': start_location,
            'end_location': end_location,
            'date': date,
        }
        return render(request, 'rides/search_results.html', context)
    return render(request, 'rides/ride_search.html')

def get_user_vehicles(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Authentication required'}, status=401)
    
    vehicles = Vehicle.objects.filter(owner=request.user)
    data = [{
        'id': vehicle.id,
        'brand': vehicle.brand.name if vehicle.brand else '',
        'model': vehicle.model.name if vehicle.model else '',
        'license_plate': vehicle.license_plate,
        'seats': vehicle.seats
    } for vehicle in vehicles]
    
    return JsonResponse(data, safe=False)

class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'rides/booking_list.html'
    context_object_name = 'bookings'

    def get_queryset(self):
        return Booking.objects.filter(passenger=self.request.user).select_related('ride')

@login_required
def my_bookings(request):
    """View for displaying user's bookings"""
    bookings = Booking.objects.filter(passenger=request.user).order_by('-created_at')
    
    context = {
        'bookings': bookings,
        'active_tab': 'bookings'
    }
    
    return render(request, 'rides/my_bookings.html', context)

@login_required
def book_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id)
    
    # Check if ride is already booked by user
    existing_booking = Booking.objects.filter(ride=ride, passenger=request.user).first()
    if existing_booking:
        messages.warning(request, 'You have already booked this ride.')
        return redirect('rides:ride-detail', ride_id=ride_id)
    
    # Check if ride has available seats
    if ride.available_seats <= 0:
        messages.error(request, 'Sorry, this ride is full.')
        return redirect('rides:ride-detail', ride_id=ride_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.ride = ride
            booking.passenger = request.user
            booking.status = 'pending'
            booking.save()
            
            # Update available seats
            ride.available_seats -= 1
            ride.save()
            
            messages.success(request, 'Ride booked successfully!')
            return redirect('rides:my-bookings')
    else:
        form = BookingForm(initial={'ride': ride, 'passenger': request.user})
    
    return render(request, 'rides/book_ride.html', {
        'ride': ride,
        'form': form,
    })

@login_required
def cancel_booking(request, pk):
    booking = get_object_or_404(Booking, pk=pk, passenger=request.user)
    
    # Only allow cancellation of pending bookings
    if booking.status != 'pending':
        messages.error(request, 'Only pending bookings can be cancelled.')
        return redirect('rides:my-bookings')
    
    # Update booking status
    booking.status = 'cancelled'
    booking.save()
    
    # Update available seats
    ride = booking.ride
    ride.available_seats += 1
    ride.save()
    
    messages.success(request, 'Booking cancelled successfully.')
    return redirect('rides:my-bookings')

class AllRidesView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Ride
    template_name = 'rides/all_rides.html'
    context_object_name = 'rides'
    paginate_by = 10

    def test_func(self):
        return self.request.user.role == 'admin'

    def get_queryset(self):
        return Ride.objects.all().order_by('-ride_date')
