from django.db import models

class User(models.Model):
    id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    user_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    mobile = models.CharField(max_length=20)
    image = models.CharField(max_length=255, null=True)

    class Meta:
        managed = False
        db_table = 'users'

class UserRideBook(models.Model):
    id = models.AutoField(primary_key=True)
    txtId = models.CharField(max_length=255)
    user_id = models.IntegerField()
    ride_id = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    paymentStatus = models.CharField(max_length=50)
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'user_ride_book'

class Ride(models.Model):
    fare = models.DecimalField(max_digits=10, decimal_places=2, default=0.00) 