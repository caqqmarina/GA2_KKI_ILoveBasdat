# main/views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm, WorkerRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Voucher, Promo
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import User, Worker, Transaction
from .forms import UserProfileUpdateForm, WorkerProfileUpdateForm
from services.models import ServiceCategory, Subcategory
from .forms import TransactionForm
import psycopg2
from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.hashers import check_password
from django.conf import settings
from django.contrib.auth.hashers import make_password

# def authenticate(request):
#     # Check if user is authenticated using the phone number stored in session
#     user_phone = request.session.get('user_phone')

#     if not user_phone:
#         messages.error(request, "You need to log in first.")
#         return None, False  # No user and not authenticated

#     user = User.objects.filter(phone_number=user_phone).first()
#     if not user:
#         messages.error(request, "User not found.")
#         return None, False  # User not found, not authenticated

#     # If user exists and is authenticated
#     is_worker = Worker.objects.filter(user_ptr_id=user.id).exists()

#     return user, is_worker 

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
    
# def homepage(request):
#     user_phone = request.session.get('user_phone')
#     is_authenticated = request.session.get('is_authenticated', False)
#     is_worker = request.session.get('is_worker', False)
    
#     user = User.objects.filter(phone_number=user_phone).first() if user_phone else None
    
#     # Get search parameters
#     search_query = request.GET.get('search', '').strip()
#     category_filter = request.GET.get('category', '').strip()
    
#     # Get all categories
#     categories = ServiceCategory.objects.all()
    
#     # Filter subcategories based on search
#     if search_query:
#         # Case-insensitive search that matches starting characters
#         subcategories = Subcategory.objects.filter(
#             Q(name__istartswith=search_query) | 
#             Q(category__name__istartswith=search_query)
#         )
#     elif category_filter:
#         subcategories = Subcategory.objects.filter(category__name=category_filter)
#     else:
#         subcategories = Subcategory.objects.all()
    
#     context = {
#         'user': user,
#         'is_worker': is_worker,
#         'categories': categories,
#         'subcategories': subcategories,
#         'search_query': search_query,
#         'selected_category': category_filter
#     }
    
#     return render(request, 'homepage.html', context)

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
    
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '').strip()
    
    categories = []
    subcategories = []
    
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
    
    context = {
        'user': user,
        'is_worker': is_worker,
        'categories': categories,
        'subcategories': subcategories,
        'search_query': search_query,
        'selected_category': category_filter
    }
    
    return render(request, 'homepage.html', context)

def landing_page(request):
    return render(request, 'landing.html')

# def login_view(request):
#     if request.method == 'POST':
#         phone = request.POST['phone']
#         password = request.POST['password']
        
#         user = User.objects.filter(phone_number=phone).first()
#         print("user", user)
#         if user is not None:
#             request.session['user_phone'] = user.phone_number
#             request.session['is_authenticated'] = True
#             request.session['is_worker'] = Worker.objects.filter(user_ptr_id=user.id).exists()
#             print("is_worker", request.session['is_worker'])
#             return redirect('homepage')
#         else:
#             messages.error(request, 'Invalid phone number or password.')
    
#     return render(request, 'login.html')

def login_view(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        password = request.POST['password']
        
        try:
            with psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM main_user WHERE phone_number = %s", (phone,))
                    user = cursor.fetchone()
                    
                    if user and check_password(password, user[2]):  # Assuming password is at index 2
                        # Set session data
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
    
    return render(request, 'login.html')

def logout_user(request):
    request.session.flush()
    return redirect('landing')

def register_landing(request):
    return render(request, 'register_landing.html')

# def register_user(request):
#     if request.method == 'POST':
#         form = UserRegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Registration successful. Please log in.')
#             return redirect('login')
#     else:
#         form = UserRegistrationForm()
#     return render(request, 'register_user.html', {'form': form})

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(user.password)  # Hash the password
            user.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register_user.html', {'form': form})

def register_worker(request):
    if request.method == 'POST':
        form = WorkerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.password = make_password(user.password)  # Hash the password
            user.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = WorkerRegistrationForm()
    return render(request, 'register_worker.html', {'form': form})

# def register_worker(request):
#     if request.method == 'POST':
#         form = WorkerRegistrationForm(request.POST)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Registration successful. Please log in.')
#             return redirect('login')
#     else:
#         form = WorkerRegistrationForm()
#     return render(request, 'register_worker.html', {'form': form})

# def user_profile(request):
#     profile = get_object_or_404(UserProfile, user=request.user)
#     if request.method == 'POST':
#         form = UserProfileForm(request.POST, instance=profile)
#         if form.is_valid():
#             form.save()
#             return redirect('user_profile')
#     else:
#         form = UserProfileForm(instance=profile)
#     return render(request, 'user_profile.html', {'form': form, 'profile': profile})

# def worker_profile(request):
#     profile = get_object_or_404(WorkerProfile, user=request.user)
#     if request.method == 'POST':
#         form = WorkerProfileForm(request.POST, instance=profile)
#         if form.is_valid():
#             form.save()
#             return redirect('worker_profile')
#     else:
#         form = WorkerProfileForm(instance=profile)
#     return render(request, 'worker_profile.html', {'form': form, 'profile': profile})

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
        'is_worker':is_worker
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

# def profile_view(request):
#     user = User.objects.filter(phone_number=request.session.get('user_phone')).first()
#     if not user:
#         return redirect('login')

#     is_worker = Worker.objects.filter(user_ptr_id=user.id).exists()

#     if request.method == 'POST':
#         if is_worker:
#             form = WorkerProfileUpdateForm(request.POST, instance=user.worker)
#         else:
#             form = UserProfileUpdateForm(request.POST, instance=user)
        
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'Profile updated successfully.')
#             return redirect('profile')
#     else:
#         if is_worker:
#             form = WorkerProfileUpdateForm(instance=user.worker)
#         else: 
#             form = UserProfileUpdateForm(instance=user)

#     context = {
#         'user': user,
#         'is_worker': is_worker,
#         'form': form,
#         # Placeholder values for now
#         'level': 'Bronze',
#         'mypay_balance': user.mypay_balance,
#         'rate': 0.00,
#         'completed_orders': 0,
#         'job_categories': []
#     }

#     return render(request, 'profile.html', context)

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

                worker_data = None
                if is_worker:
                    cursor.execute("""
                        SELECT bank_name, account_number, npwp, 
                               completed_orders_count, job_categories, image_url
                        FROM main_worker 
                        WHERE user_ptr_id = %s
                    """, (user_data[0],))
                    worker_data = cursor.fetchone()

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
                    'is_worker': is_worker,
                    'level': 'Bronze'  # You can add logic for level calculation
                }

                if worker_data:
                    context['user'].update({
                        'bank_name': worker_data[0],
                        'account_number': worker_data[1],
                        'npwp': worker_data[2],
                        'rate': worker_data[3],
                        'completed_orders': worker_data[4],
                        'job_categories': worker_data[5].split(',') if worker_data[5] else [],
                        'image_url': worker_data[6]
                    })

                return render(request, 'profile.html', context)

    except Exception as e:
        print(f"Profile view error: {e}")
        messages.error(request, 'Error loading profile.')
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