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

class ProfileUpdateForm(forms.Form):
    name = forms.CharField(max_length=255, required=True)
    password = forms.CharField(widget=forms.PasswordInput(), required=False)  # Optional for updates
    sex = forms.ChoiceField(choices=[('male', 'Male'), ('female', 'Female')], required=False)
    phone_number = forms.CharField(max_length=20, required=True)
    birth_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    address = forms.CharField(widget=forms.Textarea, required=False)

    # Worker-specific fields
    bank_name = forms.ChoiceField(choices=[
        ('GoPay', 'GoPay'),
        ('OVO', 'OVO'),
        ('Virtual Account BCA', 'Virtual Account BCA'),
        ('Virtual Account BNI', 'Virtual Account BNI'),
        ('Virtual Account Mandiri', 'Virtual Account Mandiri')
    ], required=False)
    account_number = forms.CharField(max_length=30, required=False)
    npwp = forms.CharField(max_length=20, required=False)

    def update(self, user_id):
        data = self.cleaned_data
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE main_user
                    SET name = %s, sex = %s, phone_number = %s, birth_date = %s, address = %s
                    WHERE id = %s
                """, (data['name'], data['sex'], data['phone_number'], data['birth_date'], data['address'], user_id))
                conn.commit()


class TransactionForm(forms.Form):
    TRANSACTION_CHOICES = [
        ('topup', 'TopUp MyPay'),
        ('service_payment', 'Service Payment'),
        ('transfer', 'Transfer MyPay'),
        ('withdrawal', 'Withdrawal'),
    ]

    transaction_type = forms.ChoiceField(choices=TRANSACTION_CHOICES, required=True)
    amount = forms.DecimalField(decimal_places=2, max_digits=10)
    category = forms.CharField(max_length=255, required=False)
    recipient_phone = forms.CharField(max_length=20, required=False)
    service_session = forms.IntegerField(required=False)  # Use IDs for Service Sessions
    bank_name = forms.ChoiceField(choices=[
        ('GoPay', 'GoPay'),
        ('OVO', 'OVO'),
        ('Virtual Account BCA', 'Virtual Account BCA'),
        ('Virtual Account BNI', 'Virtual Account BNI'),
        ('Virtual Account Mandiri', 'Virtual Account Mandiri')
    ], required=False)
    bank_account_number = forms.CharField(max_length=30, required=False)

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

    def save(self, user_id):
        data = self.cleaned_data
        query = """
            INSERT INTO transaction (user_id, transaction_type, amount, category, recipient_phone, service_session, bank_name, bank_account_number)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            user_id,
            data['transaction_type'],
            data['amount'],
            data.get('category'),
            data.get('recipient_phone'),
            data.get('service_session'),
            data.get('bank_name'),
            data.get('bank_account_number'),
        )
        UserRegistrationForm.execute_query(query, params)