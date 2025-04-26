from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from django.db import models

class CustomUserCreationForm(UserCreationForm):
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    email = forms.EmailField(
        max_length=254,
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control form-control-user'})
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-user'})
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-user'})
    )
    
    role = forms.ChoiceField(
        choices=CustomUser.ROLE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    phone_number = forms.CharField(
        max_length=17,
        required=True,
        validators=[phone_regex],
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Phone Number (e.g. +919876543210)'
        })
    )
    
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['class'] = 'form-control form-control-user'

class CustomUserChangeForm(UserChangeForm):
    bio = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )
    
    address = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control form-control-user'}),
        required=False
    )
    
    profile_picture = forms.ImageField(
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        required=False
    )
    
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name', 'phone_number', 'bio', 'address', 'profile_picture')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if 'class' not in self.fields[field].widget.attrs:
                self.fields[field].widget.attrs['class'] = 'form-control form-control-user'

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Enter Username, Email, or Phone Number'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-user',
            'placeholder': 'Password'
        })
    )

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username and password:
            # Convert username to lowercase for case-insensitive comparison
            username = username.lower().strip()
            
            try:
                # Try to find the user first
                user = CustomUser.objects.get(
                    models.Q(username__iexact=username) |
                    models.Q(email__iexact=username) |
                    models.Q(phone_number=username)
                )
                
                # Now try to authenticate
                if user.check_password(password):
                    self.user_cache = user
                else:
                    raise forms.ValidationError(
                        "The password you entered is incorrect. Please try again.",
                        code='invalid_password'
                    )
            except CustomUser.DoesNotExist:
                raise forms.ValidationError(
                    "No account found with this username/email/phone. Please check your credentials or register.",
                    code='invalid_login'
                )
            except CustomUser.MultipleObjectsReturned:
                # This should not happen due to unique constraints, but just in case
                raise forms.ValidationError(
                    "Multiple accounts found. Please use your username to log in.",
                    code='multiple_users'
                )
            except Exception as e:
                raise forms.ValidationError(
                    "An error occurred during login. Please try again.",
                    code='login_error'
                )
        else:
            raise forms.ValidationError(
                "Please enter both username and password.",
                code='missing_fields'
            )
            
        return self.cleaned_data

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'bio', 'address', 'profile_picture')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
            
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.lower()
        return email