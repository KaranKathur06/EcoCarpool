from django.db import models
from rides.models import Booking
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from decimal import Decimal
from users.models import CustomUser
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
import secrets
from datetime import datetime

User = get_user_model()

def generate_transaction_id():
    """Generate a unique transaction ID"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_part = secrets.token_hex(6).upper()
    return f"TXN{timestamp}{random_part}"

class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('partially_refunded', 'Partially Refunded'),
    ]
    
    PAYMENT_TYPE_CHOICES = [
        ('booking', 'Booking Payment'),
        ('tip', 'Tip'),
        ('refund', 'Refund'),
        ('penalty', 'Penalty'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payments')
    payer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payments_made')
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payments_received')
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    platform_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    processing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES, default='booking')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, unique=True, null=True, blank=True, default=None)
    gateway_transaction_id = models.CharField(max_length=200, blank=True)
    gateway_response = models.JSONField(default=dict, blank=True)
    failure_reason = models.TextField(blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    refund_reason = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'payments_payment'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['payer', 'status']),
            models.Index(fields=['transaction_id']),
        ]

    def __str__(self):
        return f"Payment {self.transaction_id} - ₹{self.amount} from {self.payer.username}"

    def save(self, *args, **kwargs):
        if not self.transaction_id:
            self.transaction_id = generate_transaction_id()
        
        # Calculate net amount
        self.net_amount = self.amount - self.platform_fee - self.processing_fee
        
        super().save(*args, **kwargs)

    def process_payment(self):
        """Process the payment"""
        if self.status != 'pending':
            raise ValidationError("Payment can only be processed from pending status.")
        
        self.status = 'processing'
        self.save()
        
        # Here you would integrate with payment gateway
        # For now, we'll simulate success
        self.status = 'completed'
        self.processed_at = timezone.now()
        self.save()
        
        return True

    def refund_payment(self, amount=None, reason=""):
        """Refund the payment"""
        if self.status != 'completed':
            raise ValidationError("Only completed payments can be refunded.")
        
        refund_amount = amount or self.amount
        if refund_amount > self.amount:
            raise ValidationError("Refund amount cannot exceed payment amount.")
        
        self.refund_amount = refund_amount
        self.refund_reason = reason
        
        if refund_amount == self.amount:
            self.status = 'refunded'
        else:
            self.status = 'partially_refunded'
        
        self.save()
        return True

    def get_status_display_class(self):
        """Get CSS class for status display"""
        status_classes = {
            'pending': 'badge-warning',
            'processing': 'badge-info',
            'completed': 'badge-success',
            'failed': 'badge-danger',
            'cancelled': 'badge-secondary',
            'refunded': 'badge-dark',
            'partially_refunded': 'badge-warning',
        }
        return status_classes.get(self.status, 'badge-secondary')

class UserPayment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    PAYMENT_METHODS = [
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('wallet', 'Wallet'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default='card')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - ₹{self.amount}"

class UserRideTip(models.Model):
    id = models.AutoField(primary_key=True)
    txtId = models.CharField(max_length=255, null=True, blank=True)
    user_id = models.IntegerField(null=True, blank=True)
    ride_id = models.IntegerField(null=True, blank=True)
    book_ride_id = models.IntegerField(null=True, blank=True)
    card_id = models.IntegerField(null=True, blank=True)
    tip_price = models.CharField(max_length=255, null=True, blank=True)
    stripe_percentage = models.CharField(max_length=255, null=True, blank=True)
    transaction_charges = models.CharField(max_length=255, null=True, blank=True)
    actual_tip_price = models.CharField(max_length=255, null=True, blank=True)
    transactionDate = models.CharField(max_length=255, null=True, blank=True)
    paymentStatus = models.CharField(max_length=255, null=True, blank=True)
    failurecode = models.CharField(max_length=255, null=True, blank=True)
    failure_message = models.CharField(max_length=255, null=True, blank=True)
    device_type = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'user_ride_tip'
        managed = False

class RidePayout(models.Model):
    id = models.AutoField(primary_key=True)
    ride_id = models.IntegerField(null=True, blank=True)
    ride_amount = models.CharField(max_length=255, null=True, blank=True)
    cancellation_amount = models.CharField(max_length=255, null=True, blank=True)
    total_amount = models.CharField(max_length=255, null=True, blank=True)
    ecp_percentage = models.CharField(max_length=255, null=True, blank=True)
    ecp_charges = models.CharField(max_length=255, null=True, blank=True)
    account_volume = models.CharField(max_length=255, null=True, blank=True)
    payoutfees = models.CharField(max_length=255, null=True, blank=True)
    payout_amount = models.CharField(max_length=255, null=True, blank=True)
    payout_total_amount = models.CharField(max_length=255, null=True, blank=True)
    stripetostripe = models.CharField(max_length=255, null=True, blank=True)
    stos_id = models.CharField(max_length=255, null=True, blank=True)
    stos_date = models.CharField(max_length=255, null=True, blank=True)
    stripetobank = models.CharField(max_length=255, null=True, blank=True)
    stob_id = models.CharField(max_length=255, null=True, blank=True)
    stob_date = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'ride_payout'
        managed = False

class Wallet(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0, validators=[MinValueValidator(0)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Wallet"

    def add_money(self, amount):
        self.balance += amount
        self.save()

    def withdraw_money(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            self.save()
            return True
        return False

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_wallet(sender, instance, **kwargs):
    if not hasattr(instance, 'wallet'):
        Wallet.objects.create(user=instance)
    instance.wallet.save()

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('DEPOSIT', 'Deposit'),
        ('WITHDRAWAL', 'Withdrawal'),
        ('PAYMENT', 'Payment'),
        ('REFUND', 'Refund'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=50, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_type} - ₹{self.amount}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on creation
            if self.transaction_type == 'DEPOSIT':
                self.wallet.add_money(self.amount)
            elif self.transaction_type == 'WITHDRAWAL':
                if not self.wallet.withdraw_money(self.amount):
                    raise ValueError("Insufficient balance")
        super().save(*args, **kwargs)

class BankAccount(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bank_accounts')
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    account_holder_name = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=11)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"

    def save(self, *args, **kwargs):
        if self.is_default:
            # Set all other accounts as non-default
            BankAccount.objects.filter(user=self.user).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)