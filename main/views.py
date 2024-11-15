from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrationForm, WorkerRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import User, Worker

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