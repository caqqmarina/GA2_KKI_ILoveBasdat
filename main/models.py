# main/models.py
from django.db import models

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
