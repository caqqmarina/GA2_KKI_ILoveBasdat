# main/views.py
from django.shortcuts import render

# main/views.py
def homepage(request):
    return render(request, 'homepage.html')

def landing_page(request):
    return render(request, 'landing.html')

def login_view(request):
    return render(request, 'login.html')

def register_landing(request):
    return render(request, 'register_landing.html')