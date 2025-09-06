"""
Custom validators for EcoCarpool application
"""
import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator


def validate_phone_number(value):
    """Validate phone number format"""
    phone_regex = re.compile(r'^\+?1?\d{9,15}$')
    if not phone_regex.match(value):
        raise ValidationError(
            _('Phone number must be in format: +1234567890. Up to 15 digits allowed.'),
            code='invalid_phone'
        )


def validate_license_plate(value):
    """Validate license plate format"""
    # Common license plate patterns
    patterns = [
        r'^[A-Z]{2}\d{2}[A-Z]{2}\d{4}$',  # Indian format: MH12AB1234
        r'^[A-Z]{3}\d{3}$',               # Simple format: ABC123
        r'^[A-Z]{2}\d{4}$',               # Format: AB1234
        r'^[A-Z]\d{3}[A-Z]{3}$',          # Format: A123BCD
    ]
    
    value = value.upper().replace(' ', '').replace('-', '')
    
    for pattern in patterns:
        if re.match(pattern, value):
            return
    
    raise ValidationError(
        _('Invalid license plate format. Please enter a valid license plate.'),
        code='invalid_license_plate'
    )


def validate_file_size(value, max_size_mb=5):
    """Validate file size"""
    max_size = max_size_mb * 1024 * 1024  # Convert MB to bytes
    if value.size > max_size:
        raise ValidationError(
            f'File size must be no more than {max_size_mb}MB.',
            code='file_too_large'
        )


def validate_image_file(value):
    """Validate image file type and size"""
    import os
    from django.conf import settings
    
    # Check file extension
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    
    if ext not in valid_extensions:
        raise ValidationError(
            _('Only image files (JPG, PNG, GIF, WebP) are allowed.'),
            code='invalid_image_type'
        )
    
    # Check file size (5MB limit)
    validate_file_size(value, 5)


def validate_document_file(value):
    """Validate document file type and size"""
    import os
    
    # Check file extension
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = ['.pdf', '.doc', '.docx']
    
    if ext not in valid_extensions:
        raise ValidationError(
            _('Only PDF and Word documents are allowed.'),
            code='invalid_document_type'
        )
    
    # Check file size (10MB limit for documents)
    validate_file_size(value, 10)


class AlphanumericValidator:
    """Validator for alphanumeric strings with optional special characters"""
    
    def __init__(self, allow_spaces=True, allow_hyphens=True):
        self.allow_spaces = allow_spaces
        self.allow_hyphens = allow_hyphens
        
    def __call__(self, value):
        pattern = r'^[a-zA-Z0-9'
        if self.allow_spaces:
            pattern += r'\s'
        if self.allow_hyphens:
            pattern += r'\-'
        pattern += r']+$'
        
        if not re.match(pattern, value):
            raise ValidationError(
                _('Only letters, numbers, spaces, and hyphens are allowed.'),
                code='invalid_characters'
            )


# Pre-configured validators
license_plate_validator = RegexValidator(
    regex=r'^[A-Z0-9\s\-]{4,15}$',
    message='Enter a valid license plate number.',
    code='invalid_license_plate'
)

indian_phone_validator = RegexValidator(
    regex=r'^\+91[6-9]\d{9}$',
    message='Enter a valid Indian phone number (+91XXXXXXXXXX).',
    code='invalid_indian_phone'
)
