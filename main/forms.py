from django import forms
from django.contrib.auth.models import User  # No Worker model here
# from .models import UserProfile, WorkerProfile  # Import your custom models
from django.contrib.auth.hashers import make_password
from .models import User, Worker, Transaction
from services.models import ServiceSession 

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
            user.mypay_balance = 0
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

class TransactionForm(forms.ModelForm):
    TRANSACTION_CHOICES = [
        ('topup', 'TopUp MyPay'),
        ('service_payment', 'Service Payment'),
        ('transfer', 'Transfer MyPay'),
        ('withdrawal', 'Withdrawal'),
    ]

    transaction_type = forms.ChoiceField(choices=TRANSACTION_CHOICES, required=True)
    recipient_phone = forms.CharField(max_length=20, required=False)
    service_session = forms.ModelChoiceField(queryset=ServiceSession.objects.none(), required=False)
    bank_name = forms.ChoiceField(choices=[('GoPay', 'GoPay'), ('OVO', 'OVO'), ('Virtual Account BCA', 'Virtual Account BCA'), ('Virtual Account BNI', 'Virtual Account BNI'), ('Virtual Account Mandiri', 'Virtual Account Mandiri')], required=False)
    bank_account_number = forms.CharField(max_length=30, required=False)

    class Meta:
        model = Transaction
        fields = ["transaction_type", "amount", "category", "recipient_phone", "service_session", "bank_name", "bank_account_number"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['service_session'].queryset = ServiceSession.objects.filter(user=user)

        self.fields['transaction_type'].widget.attrs.update({'onchange': 'updateFormFields()'})

    def clean(self):
        cleaned_data = super().clean()
        transaction_type = cleaned_data.get('transaction_type')

        if transaction_type == 'service_payment' and not cleaned_data.get('service_session'):
            self.add_error('service_session', 'This field is required for service payment.')

        if transaction_type == 'transfer' and not cleaned_data.get('recipient_phone'):
            self.add_error('recipient_phone', 'This field is required for transfer.')

        if transaction_type == 'withdrawal':
            if not cleaned_data.get('bank_name'):
                self.add_error('bank_name', 'This field is required for withdrawal.')
            if not cleaned_data.get('bank_account_number'):
                self.add_error('bank_account_number', 'This field is required for withdrawal.')

        return cleaned_data
        