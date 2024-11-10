# main/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm, WorkerRegistrationForm

# main/views.py
def homepage(request):
    return render(request, 'homepage.html')

def landing_page(request):
    return render(request, 'landing.html')

def login_view(request):
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