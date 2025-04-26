from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Vehicle, VehicleDocument, VehicleType, VehicleCompany, VehicleModel
from .forms import VehicleForm, VehicleDocumentForm
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.forms import modelformset_factory
from django.db import transaction
from django.core.paginator import Paginator
from django.core.cache import cache
from django.views.decorators.http import require_GET
from django.core.exceptions import ValidationError
import json
from django.db.models import Q

class VehicleListView(LoginRequiredMixin, ListView):
    model = Vehicle
    template_name = 'vehicles/vehicle_list.html'
    context_object_name = 'vehicles'
    ordering = ['-created_at']

    def get_queryset(self):
        return Vehicle.objects.filter(owner=self.request.user)

class VehicleDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Vehicle
    template_name = 'vehicles/vehicle_detail.html'

    def test_func(self):
        vehicle = self.get_object()
        return self.request.user == vehicle.owner

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['documents'] = self.object.vehicledocument_set.all()
        context['document_form'] = VehicleDocumentForm()
        return context

class VehicleCreateView(LoginRequiredMixin, CreateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicles/vehicle_form.html'
    success_url = reverse_lazy('vehicles:vehicle-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add New Vehicle'
        context['button_text'] = 'Add Vehicle'
        return context

class VehicleUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Vehicle
    form_class = VehicleForm
    template_name = 'vehicles/vehicle_form.html'

    def test_func(self):
        vehicle = self.get_object()
        return self.request.user == vehicle.owner

    def get_success_url(self):
        return reverse('vehicles:vehicle-detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Vehicle'
        context['button_text'] = 'Update Vehicle'
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Vehicle updated successfully!')
        return response

class VehicleDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Vehicle
    template_name = 'vehicles/vehicle_confirm_delete.html'
    success_url = reverse_lazy('vehicles:vehicle-list')

    def test_func(self):
        vehicle = self.get_object()
        return self.request.user == vehicle.owner

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Vehicle deleted successfully!')
        return super().delete(request, *args, **kwargs)

@login_required
def add_document(request, vehicle_pk):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk, owner=request.user)
    
    if request.method == 'POST':
        form = VehicleDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.vehicle = vehicle
            document.save()
            messages.success(request, 'Document uploaded successfully!')
            return redirect('vehicles:vehicle-detail', pk=vehicle.pk)
    else:
        form = VehicleDocumentForm()
    
    return render(request, 'vehicles/document_form.html', {
        'form': form,
        'vehicle': vehicle,
        'title': 'Add Document'
    })

@login_required
def delete_document(request, pk):
    document = get_object_or_404(VehicleDocument, pk=pk)
    vehicle = document.vehicle
    
    if request.user != vehicle.owner:
        messages.error(request, "You don't have permission to delete this document.")
        return redirect('vehicles:vehicle-detail', pk=vehicle.pk)
    
    document.delete()
    messages.success(request, 'Document deleted successfully!')
    return redirect('vehicles:vehicle-detail', pk=vehicle.pk)

@login_required
def get_vehicle_brands(request, vehicle_type):
    """API endpoint to get vehicle brands based on vehicle type."""
    brands = VehicleBrand.objects.filter(
        vehicle_type=vehicle_type,
        is_active=True
    ).values('id', 'name').order_by('name')
    return JsonResponse(list(brands), safe=False)

@require_GET
def get_vehicle_models(request, company_id):
    """API endpoint to get vehicle models based on company."""
    try:
        models = list(VehicleModel.objects.filter(
            company_id=company_id,
            is_active=True
        ).values('id', 'name'))
        
        return JsonResponse(models, safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
def get_vehicle_types(request):
    """API endpoint to get all vehicle types."""
    try:
        cache_key = 'vehicle_types'
        types = cache.get(cache_key)

        if types is None:
            types = list(VehicleType.objects.all().values('id', 'name', 'description'))
            cache.set(cache_key, types, timeout=3600)  # Cache for 1 hour

        return JsonResponse({
            'status': 'success',
            'data': types
        })
    except Exception as e:
        return JsonResponse({'error': 'Internal server error'}, status=500)

@login_required
def vehicle_list(request):
    vehicles = Vehicle.objects.select_related('model', 'model__company', 'model__type').all()
    return render(request, 'vehicles/vehicle_list.html', {'vehicles': vehicles})

@login_required
def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    documents = VehicleDocument.objects.filter(vehicle=vehicle)
    return render(request, 'vehicles/vehicle_detail.html', {
        'vehicle': vehicle,
        'documents': documents
    })

@login_required
def add_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user
            vehicle.save()
            return redirect('vehicle_list')
    else:
        form = VehicleForm()
    
    vehicle_types = VehicleType.objects.all()
    return render(request, 'vehicles/vehicle_form.html', {
        'form': form,
        'vehicle_types': vehicle_types
    })

@login_required
def edit_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            return redirect('vehicle_list')
    else:
        form = VehicleForm(instance=vehicle)
    
    vehicle_types = VehicleType.objects.all()
    return render(request, 'vehicles/vehicle_form.html', {
        'form': form,
        'vehicle_types': vehicle_types,
        'edit_mode': True
    })

@login_required
def vehicle_delete(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, owner=request.user)
    if request.method == 'POST':
        vehicle.delete()
        messages.success(request, 'Vehicle deleted successfully!')
        return redirect('vehicles:vehicle-list')
    return render(request, 'vehicles/vehicle_confirm_delete.html', {'vehicle': vehicle})

@login_required
def add_vehicle_document(request, vehicle_pk):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_pk, owner=request.user)
    if request.method == 'POST':
        form = VehicleDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            document = form.save(commit=False)
            document.vehicle = vehicle
            document.save()
            messages.success(request, 'Document added successfully!')
            return redirect('vehicles:vehicle-detail', pk=vehicle.pk)
    else:
        form = VehicleDocumentForm()
    
    return render(request, 'vehicles/document_form.html', {
        'form': form,
        'vehicle': vehicle
    })

def get_companies_by_type(request):
    vehicle_type_id = request.GET.get('type_id')
    if not vehicle_type_id:
        return JsonResponse({'error': 'Vehicle type is required'}, status=400)
    
    try:
        # Get unique companies that have models of the selected type
        companies = VehicleCompany.objects.filter(
            vehiclemodel__type_id=vehicle_type_id,
            vehiclemodel__is_active=True
        ).distinct().values('id', 'company_name', 'country_of_origin')
        
        return JsonResponse(list(companies), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_models_by_company(request):
    company_id = request.GET.get('company_id')
    vehicle_type_id = request.GET.get('type_id')
    
    if not company_id or not vehicle_type_id:
        return JsonResponse({'error': 'Both company and vehicle type are required'}, status=400)
    
    try:
        models = VehicleModel.objects.filter(
            company_id=company_id,
            type_id=vehicle_type_id,
            is_active=True
        ).values('id', 'model_name', 'year_from', 'year_to', 'base_price')
        
        return JsonResponse(list(models), safe=False)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
