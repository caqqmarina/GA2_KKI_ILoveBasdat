from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    MALE = 'male'
    FEMALE = 'female'
    SEX_CHOICES = [
        (MALE, 'Male'),
        (FEMALE, 'Female'),
    ]

    name = models.CharField(max_length=255)
    sex = models.CharField(max_length=10, choices=SEX_CHOICES)
    phone_number = models.CharField(max_length=20, unique=True)
    birth_date = models.DateField()
    address = models.TextField()
    last_login = models.DateTimeField(null=True, blank=True)
    groups = models.ManyToManyField(Group, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_set')

class Worker(User):
    bank_name = models.CharField(max_length=50, choices=[('GoPay', 'GoPay'), ('OVO', 'OVO'), ('Virtual Account BCA', 'Virtual Account BCA'), ('Virtual Account BNI', 'Virtual Account BNI'), ('Virtual Account Mandiri', 'Virtual Account Mandiri')])
    account_number = models.CharField(max_length=30)
    npwp = models.CharField(max_length=20, unique=True)
    image_url = models.URLField(blank=True, null=True)