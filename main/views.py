# main/views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import TransactionForm, UserRegistrationForm, WorkerRegistrationForm
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
from psycopg2.errors import UniqueViolation, RaiseException
import psycopg2
from django.http import JsonResponse
from django.conf import settings
import json


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
                
                # Fetch user's mypay_balance as an integer
                cursor.execute("SELECT mypay_balance FROM main_user WHERE id = %s", (user[0],))
                mypay_balance = cursor.fetchone()[0]
                
                # Return user with mypay_balance
                user = list(user)
                user.append(mypay_balance)
                
                return user, is_worker
    except psycopg2.Error as e:
        messages.error(request, f"Database error: {e}")
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
    user_phone = request.session.get('user_phone')
    is_worker = request.session.get('is_worker', False)
    user_name = None

    if user_phone:
        try:
            with psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            ) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT name FROM main_user WHERE phone_number = %s", (user_phone,))
                    user_data = cursor.fetchone()
                    if user_data:
                        user_name = user_data[0]
        except Exception as e:
            print(f"Error fetching user data: {e}")

    context = {
        'user_name': user_name,
        'is_worker': is_worker,
    }
    return render(request, 'landing.html', context)

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
            except RaiseException as e:
                conn.rollback()
                error_message = str(e).split('\n')[1]  # Extract the error message
                messages.error(request, f'Registration error: {error_message}')
            except UniqueViolation as e:
                conn.rollback()
                error_message = str(e).split('\n')[1]  # Extract the error message
                messages.error(request, f'Registration error: {error_message}')
            except Exception as e:
                conn.rollback()
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
            except RaiseException as e:
                conn.rollback()
                error_message = str(e).split('\n')[1]  # Extract the error message
                messages.error(request, f'Registration error: {error_message}')
            except UniqueViolation as e:
                conn.rollback()
                error_message = str(e).split('\n')[1]  # Extract the error message
                messages.error(request, f'Registration error: {error_message}')
            except Exception as e:
                conn.rollback()
                print(f"Registration error: {e}")
                messages.error(request, 'An error occurred during registration.')
    else:
        form = WorkerRegistrationForm()
    return render(request, 'register_worker.html', {'form': form})

def discount_page(request):
    user, is_worker = authenticate(request)  # Check authentication

    if not user:
        return redirect('login')  # Redirect to login if not authenticated

    try:
        # Establish database connection
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                # Query to fetch promos
                cursor.execute("SELECT id, code, offer_end_date, discount_amount FROM main_promo")
                promos = cursor.fetchall()

                # Query to fetch vouchers
                cursor.execute("""
                    SELECT id, code, discount, min_transaction, validity_days, user_quota, price
                    FROM main_voucher
                """)
                vouchers = cursor.fetchall()

        # Prepare data in a structured format
        promo_data = [
            {
                'id': promo[0],
                'code': promo[1],
                'offer_end_date': promo[2],
                'discount_amount': promo[3]
            }
            for promo in promos
        ]

        voucher_data = [
            {
                'id': voucher[0],
                'code': voucher[1],
                'discount': voucher[2],
                'min_transaction': voucher[3],
                'validity_days': voucher[4],
                'user_quota': voucher[5],
                'price': voucher[6]
            }
            for voucher in vouchers
        ]

        # Context to pass to template
        context = {
            'user': user,
            'is_worker': is_worker,
            'promos': promo_data,
            'vouchers': voucher_data,
            'user_name' : user[1]
        }

        return render(request, 'discount.html', context)

    except Exception as e:
        print(f"Error occurred: {e}")
        return redirect('error_page')

def validate_discount(request):
    user, is_worker = authenticate(request)  # Check authentication

    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body)
            discount_code = data.get('discount_code')  # Get the discount code from the JSON payload
            user_id = user[0]  # Assuming the user ID is passed in the request to validate the user's purchase

            if not discount_code or not user_id:
                return JsonResponse({'valid': False, 'message': 'Discount code or user ID not provided'}, status=400)

            # Establish database connection using psycopg2
            with psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            ) as conn:
                with conn.cursor() as cursor:
                    # Check if the code exists in the main_promo table
                    cursor.execute("SELECT discount_amount FROM main_promo WHERE code = %s", (discount_code,))
                    promo = cursor.fetchone()

                    # Check if the code exists in the main_voucher table
                    cursor.execute("SELECT id, discount, validity_days FROM main_voucher WHERE code = %s", (discount_code,))
                    voucher = cursor.fetchone()

                    if promo:
                        # Valid promo code
                        return JsonResponse({
                            'valid': True,
                            'discount_amount': promo[0],
                            'type': 'promo',  # Indicate it's a promo
                        })
                    elif voucher:
                        # Valid voucher code, now check if the user has purchased this voucher
                        voucher_id = voucher[0]
                        cursor.execute("""
                            SELECT user_quota, validity_date FROM voucher_purchases
                            WHERE user_id = %s AND voucher_id = %s
                        """, (user_id, voucher_id))

                        result = cursor.fetchone()

                        if result:
                            user_quota, validity_date = result
                            # Check if the voucher has expired
                            if validity_date < datetime.date.today():
                                return JsonResponse({
                                    'valid': False,
                                    'message': 'This voucher has expired.'
                                })

                            if user_quota > 0:
                                # Decrease the user's quota by 1
                                cursor.execute("""
                                    UPDATE voucher_purchases
                                    SET user_quota = user_quota - 1
                                    WHERE user_id = %s AND voucher_id = %s
                                """, (user_id, voucher_id))
                                conn.commit()

                                return JsonResponse({
                                    'valid': True,
                                    'discount_amount': voucher[1],
                                    'type': 'voucher',  # Indicate it's a voucher
                                    'message': f'Voucher applied successfully! You saved ${voucher[1]}'
                                })
                            else:
                                # User has no remaining quota
                                return JsonResponse({
                                    'valid': False,
                                    'message': 'You have no remaining quota for this voucher.'
                                })
                        else:
                            # User has not purchased the voucher
                            return JsonResponse({
                                'valid': False,
                                'message': 'You have not purchased this voucher.'
                            })

                    else:
                        # Invalid discount code
                        return JsonResponse({
                            'valid': False,
                            'message': 'Invalid discount code.'
                        })

        except Exception as e:
            print(f"Error occurred while validating and using the discount: {e}")
            return JsonResponse({'valid': False, 'message': 'An error occurred while processing the discount.'}, status=500)

    return JsonResponse({'valid': False, 'message': 'Invalid request method.'}, status=400)

def buy_voucher(request, voucher_id):
    user, is_worker = authenticate(request)

    if not user:
        return JsonResponse({'success': False, 'message': 'User not authenticated'}, status=403)

    if request.method == 'POST':
        try:
            # Connect to the database
            with psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            ) as conn:
                with conn.cursor() as cursor:
                    # Fetch voucher details
                    cursor.execute("SELECT id, code, price, user_quota FROM main_voucher WHERE id = %s", (voucher_id,))
                    voucher = cursor.fetchone()

                    if not voucher:
                        return JsonResponse({'success': False, 'message': 'Voucher not found'}, status=404)

                    voucher_price = voucher[2]
                    user_quota = voucher[3]

                    # Check user's balance
                    cursor.execute("SELECT mypay_balance FROM main_user WHERE id = %s", (user[0],))
                    user_balance = cursor.fetchone()[0]

                    if user_balance < voucher_price:
                        return JsonResponse({'success': False, 'message': 'Insufficient balance'}, status=400)

                    # Deduct balance and complete purchase
                    new_balance = user_balance - voucher_price
                    cursor.execute("UPDATE main_user SET mypay_balance = %s WHERE id = %s", (new_balance, user[0]))
                    # Insert a record into voucher_purchases table to track the voucher purchase
                    cursor.execute("""
                        INSERT INTO voucher_purchases (user_id, voucher_id, user_quota)
                        VALUES (%s, %s, %s)
                    """, (user[0], voucher_id, user_quota))

                    conn.commit()  # Commit the transaction

                    return JsonResponse({'success': True, 'message': 'Voucher purchased successfully'})

        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Error: {str(e)}'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)

import logging

logger = logging.getLogger(__name__)

def check_mypay_balance(request):
    user, is_worker = authenticate(request)  # Check authentication

    if not user:
        return JsonResponse({'valid': False, 'message': 'User not authenticated'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            voucher_price = data.get('voucherPrice')

            if not voucher_price:
                return JsonResponse({'valid': False, 'message': 'Voucher price not provided'}, status=400)

            # Fetch user's balance
            user_balance = user[-1]  # Assuming the last element in user is `mypay_balance`
            if user_balance >= voucher_price:
                return JsonResponse({'valid': True})
            else:
                return JsonResponse({'valid': False, 'message': 'Insufficient balance'})

        except Exception as e:
            logger.error(f"Error in check_mypay_balance: {e}")
            return JsonResponse({'valid': False, 'message': f'Error: {str(e)}'}, status=500)

    return JsonResponse({'valid': False, 'message': 'Invalid request method'}, status=400)

def some_view(request):
    user_id = request.session.get('user_id')
    user_name = get_user_name(user_id) if user_id else None

    context = {
        'user_name': user_name,
    }
    return render(request, 'template_name.html', context)

def profile_view(request, worker_id=None):
    user_phone = request.session.get('user_phone') if worker_id is None else None
    is_worker = request.session.get('is_worker', False) if worker_id is None else True
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
                cursor.execute("""
                    SELECT id, name, phone_number, sex, birth_date, address, mypay_balance, level 
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
                        'phone_number': user_data[2],
                        'sex': user_data[3],
                        'birth_date': user_data[4],
                        'address': user_data[5],
                        'mypay_balance': user_data[6],
                        'level': user_data[7]  # Include level in context
                    },
                    'user_name': user_data[1],
                    'is_worker': is_worker,
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
                    name = request.POST.get('name')
                    if not name:
                        messages.error(request, 'Name is required.')
                        return render(request, 'profile.html', context)
                        
                    password = request.POST.get('password')
                    sex = request.POST.get('sex')
                    phone_number = request.POST.get('phone_number')
                    birth_date = request.POST.get('birth_date')
                    address = request.POST.get('address')
                    image_url = request.POST.get('image_url') if is_worker else None
                    hashed_password = make_password(password) if password else user_data[2]
                    
                    if not birth_date:
                        birth_date = user_data[4]
                    
                    cursor.execute("""
                        UPDATE main_user
                        SET name = %s, password = %s, sex = %s, phone_number = %s, 
                            birth_date = %s, address = %s
                        WHERE id = %s
                    """, (name, hashed_password, sex, phone_number, birth_date, address, user_data[0]))
                    
                    if is_worker:
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
        print(f"Profile update error: {e}")
        messages.error(request, 'An error occurred while updating the profile.')
        return redirect('homepage')
    
def worker_profile(request, worker_id):
    # Get worker_id from the URL and check if the user is a worker
    is_worker = request.session.get('is_worker', False)

    try:
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                # Get user data by worker_id
                cursor.execute("""
                    SELECT id, name, phone_number, sex, address
                    FROM main_user 
                    WHERE id = %s
                """, (worker_id,))
                user_data = cursor.fetchone()

                if not user_data:
                    messages.error(request, "Worker not found.")
                    return redirect('services:worker_list')  # Redirect to worker list or any relevant page
                
                # Prepare context for template rendering
                context = {
                    'worker': {
                        'id': user_data[0],
                        'name': user_data[1],
                        'phone_number': user_data[2],
                        'sex': user_data[3],
                        'address': user_data[4],
                    },
                }
            # Render the profile page
            return render(request, 'worker_profile.html', context)
    
    except Exception as e:
        print(f"Error fetching worker details: {e}")
        messages.error(request, "An error occurred while fetching worker details.")
    
import psycopg2
from django.conf import settings
from django.shortcuts import render
from psycopg2.extras import DictCursor

def mypay(request):
    user, is_worker = authenticate(request)  # Check authentication
    # Database connection details
    try:
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            # Use DictCursor for easier access to columns by name
            with conn.cursor(cursor_factory=DictCursor) as cursor:
                # Get user details (replace '1' with a dynamic user ID if needed)
                user_query = "SELECT phone_number, mypay_balance FROM users WHERE id = %s;"
                user_id = user[0] # Replace with dynamic user ID logic if required
                cursor.execute(user_query, (user_id,))
                user = cursor.fetchone()
                if not user:
                    return render(request, 'mypay.html', {'error': 'User not found'})

                # Fetch transaction history for the user
                transaction_query = """
                    SELECT amount, date, category 
                    FROM transactions 
                    WHERE user_id = %s 
                    ORDER BY date DESC;
                """
                cursor.execute(transaction_query, (user_id,))
                transactions = cursor.fetchall()

                # Prepare context
                context = {
                    'user': {
                        'phone_number': user['phone_number'],
                        'mypay_balance': user['mypay_balance'],
                    },
                    'mypay_balance': user['mypay_balance'],
                    'transactions': [
                        {
                            'amount': t['amount'],
                            'date': t['date'],
                            'category': t['category']
                        } for t in transactions
                    ],
                }

                return render(request, 'mypay.html', context)
    except psycopg2.Error as e:
        # Log the error and return an error page
        print(f"Database error: {e}")
        return render(request, 'mypay.html', {'error': 'Database connection error'})




