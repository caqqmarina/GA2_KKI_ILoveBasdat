from django import forms
from django.contrib.auth.hashers import make_password
from django.conf import settings
import psycopg2

class UserRegistrationForm(forms.Form):
    name = forms.CharField(max_length=255)
    password = forms.CharField(widget=forms.PasswordInput())
    sex = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female')])
    phone_number = forms.CharField(max_length=20)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(widget=forms.Textarea)

    def save(self):
        data = self.cleaned_data
        hashed_password = make_password(data['password'])
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO main_user (name, password, sex, phone_number, birth_date, address, mypay_balance)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (data['name'], hashed_password, data['sex'], data['phone_number'], data['birth_date'], data['address'], 0))
                conn.commit()

class WorkerRegistrationForm(UserRegistrationForm):
    bank_name = forms.ChoiceField(choices=[('GoPay', 'GoPay'), ('OVO', 'OVO'), ('Virtual Account BCA', 'Virtual Account BCA'), ('Virtual Account BNI', 'Virtual Account BNI'), ('Virtual Account Mandiri', 'Virtual Account Mandiri')])
    account_number = forms.CharField(max_length=30)
    npwp = forms.CharField(max_length=20)
    image_url = forms.URLField(required=False)

    def save(self):
        data = self.cleaned_data
        hashed_password = make_password(data['password'])
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO main_user (name, password, sex, phone_number, birth_date, address, mypay_balance)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (data['name'], hashed_password, data['sex'], data['phone_number'], data['birth_date'], data['address'], 0))
                user_id = cursor.fetchone()[0]
                cursor.execute("""
                    INSERT INTO main_worker (user_ptr_id, bank_name, account_number, npwp, image_url)
                    VALUES (%s, %s, %s, %s, %s)
                """, (user_id, data['bank_name'], data['account_number'], data['npwp'], data['image_url']))
                conn.commit()

# class UserProfileUpdateForm(forms.ModelForm):
#     class Meta:
#         model = User
#         fields = ['name', 'sex', 'phone_number', 'birth_date', 'address']
#         widgets = {
#             'birth_date': forms.DateInput(attrs={'type': 'date'})
#         }

# class WorkerProfileUpdateForm(forms.ModelForm):
#     class Meta:
#         model = Worker 
#         fields = ['name', 'sex', 'phone_number', 'birth_date', 'address', 'bank_name', 'account_number', 'npwp', 'image_url']
#         widgets = {
#             'birth_date': forms.DateInput(attrs={'type': 'date'}),
#             'image_url': forms.URLInput(attrs={'placeholder': 'Enter image URL'})
#         }

# class TransactionForm(forms.ModelForm):
#     TRANSACTION_CHOICES = [
#         ('topup', 'TopUp MyPay'),
#         ('service_payment', 'Service Payment'),
#         ('transfer', 'Transfer MyPay'),
#         ('withdrawal', 'Withdrawal'),
#     ]

#     transaction_type = forms.ChoiceField(choices=TRANSACTION_CHOICES, required=True)
#     recipient_phone = forms.CharField(max_length=20, required=False)
#     service_session = forms.ModelChoiceField(queryset=ServiceSession.objects.none(), required=False)
#     bank_name = forms.ChoiceField(choices=[('GoPay', 'GoPay'), ('OVO', 'OVO'), ('Virtual Account BCA', 'Virtual Account BCA'), ('Virtual Account BNI', 'Virtual Account BNI'), ('Virtual Account Mandiri', 'Virtual Account Mandiri')], required=False)
#     bank_account_number = forms.CharField(max_length=30, required=False)

#     class Meta:
#         model = Transaction
#         fields = ["transaction_type", "amount", "category", "recipient_phone", "service_session", "bank_name", "bank_account_number"]

#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)
#         super().__init__(*args, **kwargs)
#         if user:
#             self.fields['service_session'].queryset = ServiceSession.objects.filter(user=user)

#         self.fields['transaction_type'].widget.attrs.update({'onchange': 'updateFormFields()'})

#     def clean(self):
#         cleaned_data = super().clean()
#         transaction_type = cleaned_data.get('transaction_type')

#         if transaction_type == 'service_payment' and not cleaned_data.get('service_session'):
#             self.add_error('service_session', 'This field is required for service payment.')

#         if transaction_type == 'transfer' and not cleaned_data.get('recipient_phone'):
#             self.add_error('recipient_phone', 'This field is required for transfer.')

#         if transaction_type == 'withdrawal':
#             if not cleaned_data.get('bank_name'):
#                 self.add_error('bank_name', 'This field is required for withdrawal.')
#             if not cleaned_data.get('bank_account_number'):
#                 self.add_error('bank_account_number', 'This field is required for withdrawal.')

#         return cleaned_data
        