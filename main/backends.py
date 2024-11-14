# main/backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import check_password
from .models import User


class PhoneNumberBackend(BaseBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(phone_number=username)  # Ensure phone_number field is correct
            if user and check_password(password, user.password):
                return user
        except User.DoesNotExist:
            return None  # User with that phone number does not exist
        return None  # Password does not match

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
