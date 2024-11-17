from django import forms
from django.contrib.auth.models import User  # No Worker model here
from .models import UserProfile, WorkerProfile  # Import your custom models
from django.contrib.auth.hashers import make_password
from .models import User, Worker

class UserRegistrationForm(forms.ModelForm):
    name = forms.CharField(max_length=150)  # Assuming "name" is a field you want to include
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User  # Link this form to the User model for name and password fields
        fields = ['username', 'password']  # Use 'username' for the User model

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.username = user.phone_number
            user.save()
        return user


class WorkerRegistrationForm(forms.ModelForm):
    bank_name = forms.ChoiceField(choices=[('GoPay', 'GoPay'), ('OVO', 'OVO'), ('Virtual Account BCA', 'Virtual Account BCA'), ('Virtual Account BNI', 'Virtual Account BNI'), ('Virtual Account Mandiri', 'Virtual Account Mandiri')])
    account_number = forms.CharField(max_length=30)
    npwp = forms.CharField(max_length=20)

    class Meta:
        model = WorkerProfile  # Correctly use WorkerProfile for Worker-specific data
        fields = ['sex', 'phone_number', 'birth_date', 'address', 'bank_name', 'account_number', 'npwp', 'image_url']
        widgets = {
            'password': forms.PasswordInput(),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ['user', 'mypay_balance', 'level']  # Exclude non-editable fields


class WorkerProfileForm(forms.ModelForm):
    class Meta:
        model = WorkerProfile
        exclude = ['user', 'mypay_balance', 'rate', 'completed_orders_count', 'job_categories']  # Exclude non-editable fields
