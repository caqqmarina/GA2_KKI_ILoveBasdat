from django.shortcuts import render, get_object_or_404, redirect
from services.models import Subcategory, Worker, Testimonial, ServiceSession, ServiceCategory
from services.forms import SubcategoryForm, CategoryForm
from django.contrib import messages
from .models import User, Worker

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

def subcategory(request, subcategory_id=None):
    user, is_worker = authenticate(request)

    if not user:  # If the user is not authenticated or doesn't exist, redirect to login
        return redirect('main:login')

    subcategory = get_object_or_404(Subcategory, pk=subcategory_id)
    
    # Fetch related data (workers, testimonials, service sessions)
    sessions = subcategory.sessions.all()
    payment_methods = dict(Worker._meta.get_field('bank_name').choices)

    context = {
        'subcategory': subcategory,
        'category': subcategory.category,  # This includes the category info
        'sessions': sessions,
        'payment_methods': payment_methods,
        'user': user,  # Pass user and worker status to the template
        'is_worker': is_worker,
    }

    return render(request, 'subcategory.html', context)


def service_bookings(request):
    user, is_worker = authenticate(request)

    if not user:  # If the user is not authenticated or doesn't exist, redirect to login
        return redirect('login')

    if request.method == "POST":
        # Handle POST request and render the service booking form or page
        return render(request, 'service_booking.html', {'user': user, 'is_worker': is_worker})

    # If GET request, just render the service booking page
    return render(request, 'service_booking.html', {'user': user, 'is_worker': is_worker})
