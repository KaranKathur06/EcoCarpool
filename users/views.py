from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic import DetailView, UpdateView, ListView, TemplateView
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ProfileUpdateForm
from .models import CustomUser
from django.db import models
from django.views.decorators.csrf import ensure_csrf_cookie

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                messages.success(request, 'Account created successfully! Please login to continue.')
                return redirect('users:login')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
        else:
            # Print form errors for debugging
            print("Form errors:", form.errors)
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})

@ensure_csrf_cookie
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:dashboard-home')
        
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = request.POST.get('remember')
            
            try:
                # Convert username to lowercase for consistency
                username = username.lower().strip()
                user = authenticate(request, username=username, password=password)
                
                if user is not None:
                    login(request, user)
                    if not remember_me:
                        request.session.set_expiry(0)
                    messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                    return redirect('dashboard:dashboard-home')
            except Exception as e:
                messages.error(request, 'An error occurred during login. Please try again.')
    else:
        form = CustomAuthenticationForm()
    
    response = render(request, 'users/login.html', {'form': form})
    response.set_cookie('csrftoken', request.META.get('CSRF_COOKIE', ''), samesite='Lax')
    return response

@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('users:login')

@method_decorator(login_required, name='dispatch')
class ProfileView(DetailView):
    model = CustomUser
    template_name = 'users/profile.html'
    context_object_name = 'user_profile'
    
    def get_object(self):
        return self.request.user
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['total_rides'] = user.get_total_rides()
        context['rating'] = user.get_rating()
        if user.is_driver:
            context['rides'] = user.get_rides_as_driver()
        else:
            context['bookings'] = user.get_bookings_as_passenger()
        return context

@method_decorator(login_required, name='dispatch')
class ProfileUpdateView(UpdateView):
    model = CustomUser
    form_class = ProfileUpdateForm
    template_name = 'users/profile_update.html'
    success_url = reverse_lazy('users:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)

@method_decorator(login_required, name='dispatch')
class UserListView(UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = 'users/user_list.html'
    context_object_name = 'users'
    paginate_by = 10
    
    def test_func(self):
        return self.request.user.is_staff
    
    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.GET.get('role')
        search = self.request.GET.get('search')
        
        if role:
            queryset = queryset.filter(role=role)
        if search:
            queryset = queryset.filter(
                models.Q(username__icontains=search) |
                models.Q(email__icontains=search) |
                models.Q(first_name__icontains=search) |
                models.Q(last_name__icontains=search)
            )
        return queryset.order_by('-registration_date')

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, 'Your account has been deleted.')
        return redirect('users:login')
    return render(request, 'users/delete_account.html')

from django.http import HttpResponse

def index(request):
    return HttpResponse("Welcome to the users app!")

def user_list(request):
    # Add your view logic here
    return render(request, 'users/user_list.html')  # Create this template

class SettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'users/settings.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

@login_required
def profile_edit(request):
    if request.method == 'POST':
        # Handle profile picture upload
        if 'profile_picture' in request.FILES:
            request.user.profile_picture = request.FILES['profile_picture']
        
        # Update other fields
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.phone_number = request.POST.get('phone_number')
        request.user.address = request.POST.get('address')
        request.user.bio = request.POST.get('bio')
        
        request.user.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('users:profile')
    
    return render(request, 'users/profile_edit.html')
