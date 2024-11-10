# main/views.py
from django.shortcuts import render

# main/views.py
def homepage(request):
    return render(request, 'homepage.html')
