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
from collections import defaultdict

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
    vehicles = Vehicle.objects.filter(owner=request.user).select_related('model', 'model__company', 'model__type')
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
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user
            vehicle.save()
            messages.success(request, 'Vehicle added successfully!')
            return redirect('vehicles:vehicle-list')
    else:
        form = VehicleForm()
    
    vehicle_types = VehicleType.objects.all().order_by('category', 'type_name')
    grouped_types = defaultdict(list)
    for vt in vehicle_types:
        grouped_types[vt.category].append(vt)
    print('DEBUG vehicle_types_grouped:', grouped_types)  # Debug print
    return render(request, 'vehicles/vehicle_form.html', {
        'form': form,
        'vehicle_types_grouped': grouped_types,
        'edit_mode': False
    })

@login_required
def edit_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vehicle updated successfully!')
            return redirect('vehicles:vehicle-list')
    else:
        form = VehicleForm(instance=vehicle)
    
    vehicle_types = VehicleType.objects.all().order_by('category', 'type_name')
    grouped_types = defaultdict(list)
    for vt in vehicle_types:
        grouped_types[vt.category].append(vt)
    return render(request, 'vehicles/vehicle_form.html', {
        'form': form,
        'vehicle_types_grouped': grouped_types,
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

@require_GET
def get_companies_by_type(request):
    vehicle_type_id = request.GET.get('type_id')
    print('DEBUG: get_companies_by_type - vehicle_type_id:', vehicle_type_id)  # Debug print
    if not vehicle_type_id:
        print('DEBUG: get_companies_by_type - No vehicle_type_id provided')
        return JsonResponse({'error': 'Vehicle type is required'}, status=400)
    try:
        # Modified query to find companies with *any* model of the given type
        companies = VehicleCompany.objects.filter(
            models__type_id=vehicle_type_id
            # Removed models__is_active=True filter here
        ).distinct().values('id', 'company_name', 'country_of_origin').order_by('company_name') # Added ordering for consistent results
        print('DEBUG: get_companies_by_type - companies found:', list(companies))  # Debug print
        return JsonResponse(list(companies), safe=False)
    except Exception as e:
        print('DEBUG: get_companies_by_type - error:', str(e))  # Debug print
        return JsonResponse({'error': str(e)}, status=500)

@require_GET
def get_models_by_company(request):
    company_id = request.GET.get('company_id')
    vehicle_type_id = request.GET.get('type_id')
    print('DEBUG: get_models_by_company - company_id:', company_id, 'vehicle_type_id:', vehicle_type_id)
    
    if not company_id or not vehicle_type_id:
        print('DEBUG: get_models_by_company - Missing company_id or vehicle_type_id')
        return JsonResponse({'error': 'Both company and vehicle type are required'}, status=400)
    
    try:
        # This query remains the same, filtering for active models of the selected company and type
        models = VehicleModel.objects.filter(
            company_id=company_id,
            type_id=vehicle_type_id,
            is_active=True
        ).values('id', 'model_name', 'year_from', 'year_to', 'base_price').order_by('model_name') # Added ordering
        
        print('DEBUG: get_models_by_company - models found:', list(models)) # Debug print
        return JsonResponse(list(models), safe=False)
    except Exception as e:
        print('DEBUG: get_models_by_company - error:', str(e)) # Debug print
        return JsonResponse({'error': str(e)}, status=500)
