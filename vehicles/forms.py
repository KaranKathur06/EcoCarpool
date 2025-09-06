from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from .models import Vehicle, VehicleDocument, VehicleType, VehicleCompany, VehicleModel
from datetime import datetime

class GroupedModelChoiceField(forms.ModelChoiceField):
    def __init__(self, queryset, group_by_field, *args, **kwargs):
        self.group_by_field = group_by_field  # Set this first!
        super().__init__(queryset, *args, **kwargs)

    @property
    def choices(self):
        grouped = {}
        for obj in self.queryset:
            group = getattr(obj, self.group_by_field)
            grouped.setdefault(group, []).append((obj.pk, str(obj)))
        choices = []
        for group, options in grouped.items():
            choices.append((group, options))
        return choices

    @choices.setter
    def choices(self, value):
        # Allow setting choices if needed (for compatibility)
        self._choices = value

class VehicleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set the queryset in __init__ to avoid database access during module import
        try:
            self.fields['vehicle_type'] = GroupedModelChoiceField(
                queryset=VehicleType.objects.all().order_by('category', 'type_name'),
                group_by_field='category',
                label='Vehicle Type',
                required=True,
                widget=forms.Select(attrs={'class': 'form-control'})
            )
        except:
            # If tables don't exist yet, create a basic field
            self.fields['vehicle_type'] = forms.ModelChoiceField(
                queryset=VehicleType.objects.none(),
                label='Vehicle Type',
                required=True,
                widget=forms.Select(attrs={'class': 'form-control'})
            )

        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['vehicle_photo']:
                field.widget.attrs['class'] = 'form-control'
            
            # Add required field indicator
            if field.required:
                field.widget.attrs['required'] = 'required'
                field.label = f"{field.label} *"

        # Set up dynamic filtering for company and model fields
        if 'vehicle_type' in self.data:
            try:
                vehicle_type_id = int(self.data.get('vehicle_type'))
                self.fields['company'].queryset = VehicleCompany.objects.filter(
                    models__type_id=vehicle_type_id,
                    is_active=True
                ).distinct().order_by('company_name')
            except (ValueError, TypeError):
                pass

        if 'company' in self.data:
            try:
                company_id = int(self.data.get('company'))
                self.fields['model'].queryset = VehicleModel.objects.filter(
                    company_id=company_id,
                    is_active=True
                ).order_by('model_name')
            except (ValueError, TypeError):
                pass

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
            'vehicle_photo',
        ]
        widgets = {
            'year': forms.NumberInput(attrs={
                'min': 1900,
                'max': timezone.now().year + 1,
                'class': 'form-control'
            }),
            'seating_capacity': forms.NumberInput(attrs={
                'min': 2,
                'max': 10,
                'class': 'form-control'
            }),
            'mileage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional'
            }),
            'vehicle_photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
        }


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
        fields = [
            'document_type',
            'document_number',
            'issue_date',
            'expiry_date',
            'document_file',
        ]
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'expiry_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'document_file': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            
            # Add required field indicator
            if field.required:
                field.widget.attrs['required'] = 'required'
                field.label = f"{field.label} *"

    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get('issue_date')
        expiry_date = cleaned_data.get('expiry_date')

        if issue_date and expiry_date and issue_date > expiry_date:
            raise forms.ValidationError("Issue date cannot be after expiry date.")

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