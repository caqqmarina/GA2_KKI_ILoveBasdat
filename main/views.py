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
    return render(request, 'homepage.html', {'user': user, 'is_worker': is_worker})

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

    # Now that the user is authenticated, you can fetch vouchers and promos
    vouchers = Voucher.objects.all()
    promos = Promo.objects.all()

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