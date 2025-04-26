from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from .models import Vehicle, VehicleDocument, VehicleType, VehicleCompany, VehicleModel
from datetime import datetime

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            'vehicle_type',
            'company',
            'model',
            'license_plate',
            'color',
            'year',
            'seating_capacity',
            'fuel_type',
            'mileage',
            'vehicle_photo'
        ]
        widgets = {
            'vehicle_type': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select vehicle type'
            }),
            'company': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select company/brand'
            }),
            'model': forms.Select(attrs={
                'class': 'form-control',
                'placeholder': 'Select vehicle model'
            }),
            'license_plate': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., GJ-01-XX-1234'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Black, White, Silver'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1900,
                'max': datetime.now().year + 1,
                'placeholder': f'Enter year (1900-{datetime.now().year + 1})'
            }),
            'seating_capacity': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 2,
                'max': 10,
                'placeholder': 'Enter number of seats (2-10)'
            }),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}),
            'mileage': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'placeholder': 'Enter mileage in km/l'
            }),
            'vehicle_photo': forms.FileInput(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add required asterisk to required fields
        for field in self.fields:
            if self.fields[field].required:
                self.fields[field].label = f"{self.fields[field].label}*"
        
        # Add help texts
        self.fields['license_plate'].help_text = "Enter vehicle registration number in correct format"
        self.fields['mileage'].help_text = "Enter mileage in kilometers per liter"
        self.fields['seating_capacity'].help_text = "Enter total number of seats including driver"
        
        # Set choices for vehicle type and company with empty option
        self.fields['vehicle_type'].queryset = VehicleType.objects.all().order_by('type_name')
        self.fields['company'].queryset = VehicleCompany.objects.all().order_by('company_name')
        
        # Add empty label for select fields
        self.fields['vehicle_type'].empty_label = "Select vehicle type"
        self.fields['company'].empty_label = "Select company/brand"
        self.fields['model'].empty_label = "Select vehicle model"
        
        # Add help text for vehicle type
        self.fields['vehicle_type'].help_text = "Select the type of vehicle you are registering"
        
        # If instance exists, filter model choices
        if self.instance.pk and self.instance.company:
            self.fields['model'].queryset = VehicleModel.objects.filter(
                company=self.instance.company
            ).order_by('name')
        else:
            self.fields['model'].queryset = VehicleModel.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        company = cleaned_data.get('company')
        model = cleaned_data.get('model')
        
        if company and model and model.company != company:
            raise forms.ValidationError({
                'model': 'Selected model does not belong to the selected company.'
            })
        
        return cleaned_data

    def clean_year(self):
        year = self.cleaned_data.get('year')
        current_year = datetime.now().year
        if year:
            if year < 1900 or year > current_year + 1:
                raise forms.ValidationError(f'Year must be between 1900 and {current_year + 1}')
        return year

    def clean_seats(self):
        seats = self.cleaned_data.get('seating_capacity')
        if seats:
            if seats < 2 or seats > 10:
                raise forms.ValidationError('Number of seats must be between 2 and 10')
        return seats

class VehicleDocumentForm(forms.ModelForm):
    class Meta:
        model = VehicleDocument
        fields = ['document_type', 'document_file', 'expiry_date']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-control'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if self.fields[field].required:
                self.fields[field].label = f"{self.fields[field].label}*"

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            # Check file extension
            ext = file.name.split('.')[-1].lower()
            if ext not in ['pdf', 'doc', 'docx']:
                raise forms.ValidationError('Only PDF and Word documents are allowed.')
            
            # Check file size (5MB limit)
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError('File size must be no more than 5MB.')
        return file 