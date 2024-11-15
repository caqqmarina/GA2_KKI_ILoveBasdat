# main/views.py
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserRegistrationForm, WorkerRegistrationForm, UserProfileForm, WorkerProfileForm, UserProfile, WorkerProfile
from django.contrib.auth.decorators import login_required

# main/views.py

@login_required(login_url='login')
def homepage(request):
    return render(request, 'homepage.html')


def landing_page(request):
    return render(request, 'landing.html')

def login_view(request):
    if request.method == 'POST':
        phone = request.POST['phone']  # Should match input name in `login.html`
        password = request.POST['password']  # Should match input name in `login.html`
        
        # Authenticate using phone as username
        user = authenticate(request, username=phone, password=password)
        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.error(request, 'Invalid phone number or password.')
    
    return render(request, 'login.html')


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

def user_profile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = UserProfileForm(instance=profile)
    return render(request, 'user_profile.html', {'form': form, 'profile': profile})

def worker_profile(request):
    profile = get_object_or_404(WorkerProfile, user=request.user)
    if request.method == 'POST':
        form = WorkerProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('worker_profile')
    else:
        form = WorkerProfileForm(instance=profile)
    return render(request, 'worker_profile.html', {'form': form, 'profile': profile})