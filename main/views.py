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
from .models import User, Worker
from .forms import UserProfileUpdateForm, WorkerProfileUpdateForm
from services.models import ServiceCategory, Subcategory
from django.db.models import Q 

def authenticate(request):
    # Check if user is authenticated using the phone number stored in session
    user_phone = request.session.get('user_phone')

    if not user_phone:
        messages.error(request, "You need to log in first.")
        return None, False  # No user and not authenticated

    user = User.objects.filter(phone_number=user_phone).first()
    if not user:
        messages.error(request, "User not found.")
        return None, False  # User not found, not authenticated

    # If user exists and is authenticated
    is_worker = Worker.objects.filter(user_ptr_id=user.id).exists()

    return user, is_worker 

def homepage(request):
    user_phone = request.session.get('user_phone')
    is_authenticated = request.session.get('is_authenticated', False)
    is_worker = request.session.get('is_worker', False)
    
    user = User.objects.filter(phone_number=user_phone).first() if user_phone else None
    
    # Get search parameters
    search_query = request.GET.get('search', '').strip()
    category_filter = request.GET.get('category', '').strip()
    
    # Get all categories
    categories = ServiceCategory.objects.all()
    
    # Filter subcategories based on search
    if search_query:
        # Case-insensitive search that matches starting characters
        subcategories = Subcategory.objects.filter(
            Q(name__istartswith=search_query) | 
            Q(category__name__istartswith=search_query)
        )
    elif category_filter:
        subcategories = Subcategory.objects.filter(category__name=category_filter)
    else:
        subcategories = Subcategory.objects.all()
    
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

def login_view(request):
    if request.method == 'POST':
        phone = request.POST['phone']
        password = request.POST['password']
        
        user = User.objects.filter(phone_number=phone).first()
        print("user", user)
        if user is not None:
            request.session['user_phone'] = user.phone_number
            request.session['is_authenticated'] = True
            request.session['is_worker'] = Worker.objects.filter(user_ptr_id=user.id).exists()
            print("is_worker", request.session['is_worker'])
            return redirect('homepage')
        else:
            messages.error(request, 'Invalid phone number or password.')
    
    return render(request, 'login.html')

def logout_user(request):
    return redirect('landing')

def register_landing(request):
    return render(request, 'register_landing.html')

def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'register_user.html', {'form': form})

def register_worker(request):
    if request.method == 'POST':
        form = WorkerRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. Please log in.')
            return redirect('login')
    else:
        form = WorkerRegistrationForm()
    return render(request, 'register_worker.html', {'form': form})

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

def profile_view(request):
    user = User.objects.filter(phone_number=request.session.get('user_phone')).first()
    if not user:
        return redirect('login')

    is_worker = Worker.objects.filter(user_ptr_id=user.id).exists()

    if request.method == 'POST':
        if is_worker:
            form = WorkerProfileUpdateForm(request.POST, instance=user.worker)
        else:
            form = UserProfileUpdateForm(request.POST, instance=user)
        
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        if is_worker:
            form = WorkerProfileUpdateForm(instance=user.worker)
        else: 
            form = UserProfileUpdateForm(instance=user)

    context = {
        'user': user,
        'is_worker': is_worker,
        'form': form,
        # Placeholder values for now
        'level': 'Bronze',
        'mypay_balance': 0.00,
        'rate': 0.00,
        'completed_orders': 0,
        'job_categories': []
    }

    return render(request, 'profile.html', context)