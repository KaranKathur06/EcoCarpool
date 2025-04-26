from django import forms
from django.utils import timezone
from .models import Ride, Booking
from vehicles.models import Vehicle

class RideForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = [
            'vehicle',
            'start_location',
            'end_location',
            'ride_date',
            'available_seats',
            'price_per_seat',
            'distance',
            'estimated_duration',
            'description',
            'is_recurring',
            'recurring_days'
        ]
        widgets = {
            'ride_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'estimated_duration': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'recurring_days': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            self.fields['vehicle'].queryset = Vehicle.objects.filter(owner=self.user)
        else:
            self.fields['vehicle'].queryset = Vehicle.objects.none()

    def clean_ride_date(self):
        ride_date = self.cleaned_data.get('ride_date')
        if ride_date and ride_date < timezone.now():
            raise forms.ValidationError("Ride date cannot be in the past")
        return ride_date

    def clean(self):
        cleaned_data = super().clean()
        start_location = cleaned_data.get('start_location')
        end_location = cleaned_data.get('end_location')
        
        if start_location and end_location and start_location == end_location:
            raise forms.ValidationError("Start and end locations cannot be the same")
            
        return cleaned_data

class RideSearchForm(forms.Form):
    start_location = forms.CharField(max_length=100, required=False)
    end_location = forms.CharField(max_length=100, required=False)
    date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    seats = forms.IntegerField(min_value=1, required=False)

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['ride', 'passenger', 'status']
        widgets = {
            'ride': forms.HiddenInput(),
            'passenger': forms.HiddenInput(),
            'status': forms.HiddenInput(),
        } 