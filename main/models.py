# main/models.py
from django.db import models
from django.contrib.auth.models import User

class User(models.Model):
    name = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    sex = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')])
    phone_number = models.CharField(max_length=20, unique=True)
    birth_date = models.DateField()
    address = models.TextField()

class Worker(User):
    bank_name = models.CharField(max_length=50, choices=[('GoPay', 'GoPay'), ('OVO', 'OVO'), ('Virtual Account BCA', 'Virtual Account BCA'), ('Virtual Account BNI', 'Virtual Account BNI'), ('Virtual Account Mandiri', 'Virtual Account Mandiri')])
    account_number = models.CharField(max_length=30)
    npwp = models.CharField(max_length=20, unique=True)
    image_url = models.URLField(blank=True, null=True)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    level = models.CharField(max_length=50, blank=True)
    sex = models.CharField(max_length=1, choices=[('M', 'M'), ('F', 'F')], blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    mypay_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, editable=False)

class WorkerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    sex = models.CharField(max_length=1, choices=[('F', 'Female'), ('M', 'Male')], blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True)
    mypay_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0, editable=False)
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=30, blank=True)
    npwp = models.CharField(max_length=30, blank=True)
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0, editable=False)
    completed_orders_count = models.IntegerField(default=0, editable=False)
    job_categories = models.TextField(blank=True)  # Store job categories as text
    image_url = models.URLField(blank=True)

class Voucher(models.Model):
    code = models.CharField(max_length=50, unique=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2)
    min_transaction = models.DecimalField(max_digits=10, decimal_places=2)
    validity_days = models.IntegerField()
    user_quota = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.code

class Promo(models.Model):
    code = models.CharField(max_length=50, unique=True)
    offer_end_date = models.DateField()

    def __str__(self):
        return self.code

