from django import forms
from .models import User, Worker

class UserRegistrationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['name', 'password', 'sex', 'phone_number', 'birth_date', 'address']
        widgets = {
            'password': forms.PasswordInput(),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

class WorkerRegistrationForm(UserRegistrationForm):
    bank_name = forms.ChoiceField(choices=[('GoPay', 'GoPay'), ('OVO', 'OVO'), ('Virtual Account BCA', 'Virtual Account BCA'), ('Virtual Account BNI', 'Virtual Account BNI'), ('Virtual Account Mandiri', 'Virtual Account Mandiri')])
    account_number = forms.CharField(max_length=30)
    npwp = forms.CharField(max_length=20)

    class Meta(UserRegistrationForm.Meta):
        model = Worker
        fields = UserRegistrationForm.Meta.fields + ['bank_name', 'account_number', 'npwp', 'image_url']
