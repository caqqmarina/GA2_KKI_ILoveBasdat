# main/views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm, WorkerRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.urls import reverse
import psycopg2
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.contrib.auth.hashers import make_password
import uuid
import logging
from .utils import get_user_name

def authenticate(request):
    user_phone = request.session.get('user_phone')
    
    if not user_phone:
        messages.error(request, "You need to log in first.")
        return None, False

    try:
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                # Check if user exists
                cursor.execute("SELECT * FROM main_user WHERE phone_number = %s", (user_phone,))
                user = cursor.fetchone()
                
                
                if not user:
                    messages.error(request, "User not found.")
                    return None, False
                
                # Check if user is a worker
                cursor.execute("SELECT EXISTS(SELECT 1 FROM main_worker WHERE user_ptr_id = %s)", (user[0],))
                is_worker = cursor.fetchone()[0]
                
                return user, is_worker
                
    except Exception as e:
        print(f"Authentication error: {e}")
        return None, False
    

def homepage(request):
    user_phone = request.session.get('user_phone')
    is_authenticated = request.session.get('is_authenticated', False)
    is_worker = request.session.get('is_worker', False)
    
    user = None
    if user_phone:
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM main_user WHERE phone_number = %s", (user_phone,))
                user = cursor.fetchone()
                if user:
                    user_name = user[1]  # Get name from user tuple
    
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '').strip()

    
    with psycopg2.connect(
        dbname=settings.DATABASES['default']['NAME'],
        user=settings.DATABASES['default']['USER'],
        password=settings.DATABASES['default']['PASSWORD'],
        host=settings.DATABASES['default']['HOST'],
        port=settings.DATABASES['default']['PORT']
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM services_servicecategory")
            categories = cursor.fetchall()

            category_dict = {}
            for category in categories:
                category_id = category[0]
                category_name = category[1]
                category_description = category[2]
                category_dict[category_id] = {
                    'name': category_name,
                    'description': category_description,
                    'subcategories': []
                }
            
            if search_query:
                cursor.execute("""
                    SELECT * FROM services_subcategory
                    WHERE name ILIKE %s OR category_id IN (
                        SELECT id FROM services_servicecategory WHERE name ILIKE %s
                    )
                """, (f'{search_query}%', f'{search_query}%'))
            elif category_filter:
                cursor.execute("""
                    SELECT * FROM services_subcategory
                    WHERE category_id IN (
                        SELECT id FROM services_servicecategory WHERE name = %s
                    )
                """, (category_filter,))
            else:
                cursor.execute("SELECT * FROM services_subcategory")
            
            subcategories = cursor.fetchall()

            for subcategory in subcategories:
                subcategory_id = subcategory[0]
                subcategory_name = subcategory[1]
                subcategory_description = subcategory[2]
                category_id = subcategory[3]

                # Add subcategory to the corresponding category
                if category_id in category_dict:
                    category_dict[category_id]['subcategories'].append({
                        'id': subcategory_id,
                        'name': subcategory_name,
                        'description': subcategory_description
                    })
                    print(category_dict)
    
    context = {
        'user': user,
        'is_worker': is_worker,
        'user_name': user_name,
        'categories': categories,
        'subcategories': subcategories,
        'search_query': search_query,
        'selected_category': category_filter,
        'categories': category_dict
    }
    
    return render(request, 'Homepage.html', context)

def landing_page(request):
    return render(request, 'landing.html')

def login_user(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        password = request.POST['password']
        
        try:
            conn = psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            )
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM main_user WHERE phone_number = %s", (phone,))
            user = cursor.fetchone()

            if user and check_password(password, user[2]):  # Assuming password is at index 2
                request.session['user_phone'] = phone
                request.session['is_authenticated'] = True
                cursor.execute("SELECT EXISTS(SELECT 1 FROM main_worker WHERE user_ptr_id = %s)", (user[0],))
                request.session['is_worker'] = cursor.fetchone()[0]
                return redirect('homepage')
            else:
                messages.error(request, 'Invalid phone number or password.')
        except Exception as e:
            print(f"Login error: {e}")
            messages.error(request, 'An error occurred during login.')
        finally:
            if 'cursor' in locals():
                cursor.close()
            if 'conn' in locals():
                conn.close()
    
    return render(request, 'login.html')

def logout_user(request):
    request.session.flush()
    return redirect('landing')

def register_landing(request):
    return render(request, 'register_landing.html')

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            hashed_password = make_password(data['password'])
            try:
                with psycopg2.connect(
                    dbname=settings.DATABASES['default']['NAME'],
                    user=settings.DATABASES['default']['USER'],
                    password=settings.DATABASES['default']['PASSWORD'],
                    host=settings.DATABASES['default']['HOST'],
                    port=settings.DATABASES['default']['PORT']
                ) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            INSERT INTO main_user (name, password, sex, phone_number, birth_date, address, date_joined, is_active, is_staff, is_superuser, mypay_balance, email, first_name, last_name, username)
                            VALUES (%s, %s, %s, %s, %s, %s, NOW(), TRUE, FALSE, FALSE, %s, %s, %s, %s, %s)
                            RETURNING id
                        """, (
                            data['name'], 
                            hashed_password, 
                            data['sex'], 
                            data['phone_number'], 
                            data['birth_date'], 
                            data['address'], 
                            0,  # Default value for mypay_balance
                            data.get('email', ''),  # Default to empty string if not provided
                            data.get('first_name', ''),  # Default to empty string if not provided
                            data.get('last_name', ''),  # Default to empty string if not provided
                            data.get('username', '')  # Default to empty string if not provided
                        ))
                        user_id = cursor.fetchone()[0]
                        conn.commit()
                messages.success(request, 'Registration successful. Please log in.')
                return redirect('login')
            except Exception as e:
                print(f"Registration error: {e}")
                messages.error(request, 'An error occurred during registration.')
    else:
        form = UserRegistrationForm()
    return render(request, 'register_user.html', {'form': form})

logger = logging.getLogger(__name__)

def generate_unique_username(cursor):
    while True:
        username = f"user_{str(uuid.uuid4())[:8]}"
        cursor.execute("SELECT 1 FROM main_user WHERE username = %s", (username,))
        if not cursor.fetchone():
            return username

def register_worker(request):
    if request.method == 'POST':
        form = WorkerRegistrationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            hashed_password = make_password(data['password'])
            try:
                with psycopg2.connect(
                    dbname=settings.DATABASES['default']['NAME'],
                    user=settings.DATABASES['default']['USER'],
                    password=settings.DATABASES['default']['PASSWORD'],
                    host=settings.DATABASES['default']['HOST'],
                    port=settings.DATABASES['default']['PORT']
                ) as conn:
                    with conn.cursor() as cursor:
                        # Generate a unique username
                        username = generate_unique_username(cursor)
                        
                        # Insert into main_user
                        cursor.execute("""
                            INSERT INTO main_user (
                                name, password, sex, phone_number, birth_date, address, 
                                date_joined, is_active, is_staff, is_superuser, 
                                mypay_balance, email, first_name, last_name, username
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, NOW(), TRUE, FALSE, FALSE, %s, %s, %s, %s, %s)
                            RETURNING id
                        """, (
                            data['name'], 
                            hashed_password, 
                            data['sex'], 
                            data['phone_number'], 
                            data['birth_date'], 
                            data['address'], 
                            0,  # Default value for mypay_balance
                            data.get('email', ''),  # Default to empty string if not provided
                            data.get('first_name', ''),  # Default to empty string if not provided
                            data.get('last_name', ''),  # Default to empty string if not provided
                            username  # Ensure username is unique
                        ))
                        user_id = cursor.fetchone()[0]
                        
                        # Insert into main_worker
                        cursor.execute("""
                            INSERT INTO main_worker (user_ptr_id, bank_name, account_number, npwp, image_url)
                            VALUES (%s, %s, %s, %s, %s)
                        """, (
                            user_id, 
                            data['bank_name'], 
                            data['account_number'], 
                            data['npwp'], 
                            data['image_url']
                        ))
                        conn.commit()
                messages.success(request, 'Registration successful. Please log in.')
                return redirect('login')
            except Exception as e:
                print(f"Registration error: {e}")
                messages.error(request, 'An error occurred during registration.')
    else:
        form = WorkerRegistrationForm()
    return render(request, 'register_worker.html', {'form': form})

def discount_page(request):
    user, is_worker = authenticate(request)  # Check authentication

    if not user:
        return redirect('login')  # Redirect to login if not authenticated

    # Hardcoded voucher data
    vouchers = [
        {
            'code': 'VOUCHER1',
            'discount': 10.00,  # 10% discount
            'min_transaction_order': 50.00,  # Minimum transaction order: $50
            'valid_days': 30,  # Valid for 30 days
            'user_quota': 100,  # Maximum 100 users can use this voucher
            'price': 5.00  # Voucher price: $5
        },
        {
            'code': 'VOUCHER2',
            'discount': 15.00,  # 15% discount
            'min_transaction_order': 100.00,  # Minimum transaction order: $100
            'valid_days': 60,  # Valid for 60 days
            'user_quota': 200,  # Maximum 200 users can use this voucher
            'price': 8.00  # Voucher price: $8
        },
        {
            'code': 'VOUCHER3',
            'discount': 20.00,  # 20% discount
            'min_transaction_order': 150.00,  # Minimum transaction order: $150
            'valid_days': 45,  # Valid for 45 days
            'user_quota': 300,  # Maximum 300 users can use this voucher
            'price': 10.00  # Voucher price: $10
        },
        {
            'code': 'VOUCHER4',
            'discount': 5.00,  # 5% discount
            'min_transaction_order': 20.00,  # Minimum transaction order: $20
            'valid_days': 15,  # Valid for 15 days
            'user_quota': 50,  # Maximum 50 users can use this voucher
            'price': 2.00  # Voucher price: $2
        }
    ]

    # Hardcoded promo data
    promos = [
        {'code': 'PROMO10', 'offer_end_date': '2024-12-31'},
        {'code': 'PROMO20', 'offer_end_date': '2024-11-30'},
        {'code': 'PROMO30', 'offer_end_date': '2024-12-15'},
    ]

    context = {
        'vouchers': vouchers,
        'promos': promos,
        'user': user,
        'is_worker':is_worker,
        'user_name': user[1],
    }
    return render(request, 'discount.html', context)

def buy_voucher(request, voucher_id):
    if request.method == 'POST':
        user = request.user
        try:
            voucher = Voucher.objects.get(id=voucher_id)
        except Voucher.DoesNotExist:
            messages.error(request, 'Voucher not found.')
            return HttpResponseRedirect(reverse('discount'))

        # Check if user has enough balance
        if user.profile.mypay_balance >= voucher.price:
            # Deduct balance
            user.profile.mypay_balance -= voucher.price
            user.profile.save()

            messages.success(request, f'You successfully bought the voucher: {voucher.code}.')
            return HttpResponseRedirect(reverse('discount'))
        else:
            messages.error(request, 'Insufficient balance to buy this voucher.')
            return HttpResponseRedirect(reverse('discount'))

    messages.error(request, 'Invalid request.')
    return HttpResponseRedirect(reverse('discount'))

def some_view(request):
    user_id = request.session.get('user_id')
    user_name = get_user_name(user_id) if user_id else None

    context = {
        'user_name': user_name,
    }
    return render(request, 'template_name.html', context)

def profile_view(request):
    user_phone = request.session.get('user_phone')
    is_worker = request.session.get('is_worker', False)
    if not user_phone:
        messages.error(request, "Please log in first")
        return redirect('login')
    try:
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                # Get user data
                cursor.execute("""
                    SELECT id, name, password, phone_number, sex, birth_date, 
                           address, mypay_balance 
                    FROM main_user 
                    WHERE phone_number = %s
                """, (user_phone,))
                user_data = cursor.fetchone()
                if not user_data:
                    messages.error(request, 'User data not found.')
                    return redirect('homepage')
                
                context = {
                    'user': {
                        'id': user_data[0],
                        'name': user_data[1],
                        'phone_number': user_data[3],
                        'sex': user_data[4],
                        'birth_date': user_data[5],
                        'address': user_data[6],
                        'mypay_balance': user_data[7]
                    },
                    'user_name': user_data[1],  
                    'is_worker': is_worker,
                    'level': 'Bronze'  # You can add logic for level calculation
                }
                if is_worker:
                    cursor.execute("""
                        SELECT bank_name, account_number, npwp, image_url
                        FROM main_worker 
                        WHERE user_ptr_id = %s
                    """, (user_data[0],))
                    worker_data = cursor.fetchone()
                    if worker_data:
                        context['user'].update({
                            'bank_name': worker_data[0],
                            'account_number': worker_data[1],
                            'npwp': worker_data[2],
                            'image_url': worker_data[3]
                        })
                if request.method == 'POST':
                    # Handle form submission
                    name = request.POST.get('name')
                    password = request.POST.get('password')
                    sex = request.POST.get('sex')
                    phone_number = request.POST.get('phone_number')
                    birth_date = request.POST.get('birth_date')
                    address = request.POST.get('address')
                    image_url = request.POST.get('image_url') if is_worker else None
                    hashed_password = make_password(password) if password else user_data[2]
                    # Update main_user
                    cursor.execute("""
                        UPDATE main_user
                        SET name = %s, password = %s, sex = %s, phone_number = %s, 
                            birth_date = %s, address = %s
                        WHERE id = %s
                    """, (name, hashed_password, sex, phone_number, birth_date, address, user_data[0]))
                    # Update main_worker if applicable
                    if is_worker:
                        # If image_url is empty, set it to NULL
                        image_url = image_url if image_url else None
                        cursor.execute("""
                            UPDATE main_worker
                            SET image_url = %s
                            WHERE user_ptr_id = %s
                        """, (image_url, user_data[0]))
                    conn.commit()
                    messages.success(request, 'Profile updated successfully.')
                    return redirect('profile')
                return render(request, 'profile.html', context)
    except Exception as e:
        logger.error(f"Profile update error: {e}", exc_info=True)
        messages.error(request, 'Error updating profile.')
        return redirect('homepage')
    
def mypay(request):
    # Dummy user data
    user = {
        'phone_number': '1234567890',
        'mypay_balance': 1000,
    }

    # Dummy transactions data
    transactions = [
        {'amount': 100, 'date': '2024-11-18', 'category': 'TopUp'},
        {'amount': 200, 'date': '2024-11-17', 'category': 'Service Payment'},
    ]

    form = TransactionForm()

    context = {
        'user': user,
        'is_worker': False,
        'mypay_balance': user['mypay_balance'],
        'transactions': transactions,
        'form': form,
    }

    return render(request, 'mypay.html', context)


