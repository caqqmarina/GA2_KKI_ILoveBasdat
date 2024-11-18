from django import forms
from django.contrib.auth.models import User  # No Worker model here
# from .models import UserProfile, WorkerProfile  # Import your custom models
from django.contrib.auth.hashers import make_password
from .models import User, Worker

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'password', 'sex', 'phone_number', 'birth_date', 'address']
        widgets = {
            'password': forms.PasswordInput(),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.username = user.phone_number
            user.save()
        return user

class WorkerRegistrationForm(UserRegistrationForm):
    bank_name = forms.ChoiceField(choices=[('GoPay', 'GoPay'), ('OVO', 'OVO'), ('Virtual Account BCA', 'Virtual Account BCA'), ('Virtual Account BNI', 'Virtual Account BNI'), ('Virtual Account Mandiri', 'Virtual Account Mandiri')])
    account_number = forms.CharField(max_length=30)
    npwp = forms.CharField(max_length=20)

    class Meta(UserRegistrationForm.Meta):
        model = Worker
        fields = UserRegistrationForm.Meta.fields + ['bank_name', 'account_number', 'npwp', 'image_url']

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'sex', 'phone_number', 'birth_date', 'address']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'})
        }

class WorkerProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Worker 
        fields = ['name', 'sex', 'phone_number', 'birth_date', 'address', 'bank_name', 'account_number', 'npwp', 'image_url']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'image_url': forms.URLInput(attrs={'placeholder': 'Enter image URL'})
        }