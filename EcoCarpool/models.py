from django.db import models
from django.utils import timezone

class UserRideBook(models.Model):
    id = models.AutoField(primary_key=True)
    txtId = models.CharField(max_length=255, null=True, blank=True)
    user_id = models.IntegerField()
    ride_id = models.IntegerField()
    from_stopover_id = models.IntegerField(null=True, blank=True)
    to_stopover_id = models.IntegerField(null=True, blank=True)
    coupon_id = models.IntegerField(null=True, blank=True)
    card_id = models.IntegerField(null=True, blank=True)
    no_of_seat = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_ride_book'

class UserPayment(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    create_link = models.CharField(max_length=255, null=True, blank=True)
    update_link = models.CharField(max_length=255, null=True, blank=True)
    account_holder_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    ssn = models.CharField(max_length=255, null=True, blank=True)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    dob = models.DateField(null=True, blank=True)
    accountnumber = models.CharField(max_length=255, null=True, blank=True)
    rountingnumber = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    state = models.CharField(max_length=255, null=True, blank=True)
    zipcode = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_payment'

class UserRideTip(models.Model):
    id = models.AutoField(primary_key=True)
    txtId = models.CharField(max_length=255, null=True, blank=True)
    user_id = models.IntegerField()
    ride_id = models.IntegerField()
    book_ride_id = models.IntegerField()
    card_id = models.IntegerField(null=True, blank=True)
    tip_price = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=255, null=True, blank=True)
    payment_status = models.CharField(max_length=50, null=True, blank=True)
    status = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_ride_tip'

class RidePayout(models.Model):
    id = models.AutoField(primary_key=True)
    ride_id = models.IntegerField()
    ride_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cancellation_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payout_status = models.CharField(max_length=50, default='pending')
    payout_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'ride_payout'

class CouponCode(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    coupon_code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    coupon_type = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    percentage = models.IntegerField(null=True, blank=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    usage_limit = models.IntegerField(null=True, blank=True)
    used_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'coupon_code' 