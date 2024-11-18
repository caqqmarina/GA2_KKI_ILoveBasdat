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

    # Handle booking (store the booked session in the session)
    if request.method == 'POST' and 'book_service' in request.POST:
        session_id = request.POST.get('session_id')
        if session_id:
            booked_sessions = request.session.get('booked_sessions', [])
            if session_id not in booked_sessions:
                booked_sessions.append(session_id)
            request.session['booked_sessions'] = booked_sessions

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

    if not user:  # Redirect to login if user is not authenticated
        return redirect('login')

    # Fetch available sessions from the database (assuming `Session` model)
    sessions = ServiceSession.objects.all()

    if request.method == "POST":
        session_id = request.POST.get('session_id')
        if not session_id:
            messages.error(request, "No session selected.")
            return redirect('services:subcategory', subcategory_id=request.session.get('subcategory_id'))

        # Store the session in a temporary list or database
        if 'booked_sessions' not in request.session:
            request.session['booked_sessions'] = []

        # Avoid duplicating the session
        if session_id not in request.session['booked_sessions']:
            request.session['booked_sessions'].append(session_id)
            request.session.modified = True

        # Redirect to service bookings page
        return redirect('services:service_bookings')

    # Retrieve booked sessions
    booked_session_ids = request.session.get('booked_sessions', [])
    booked_sessions = ServiceSession.objects.filter(id__in=booked_session_ids)
    unique_subcategories = {session.subcategory for session in booked_sessions}

    context = {
        'user': user,
        'is_worker': is_worker,
        'booked_sessions': booked_sessions,
        'unique_subcategories': unique_subcategories,
    }
        
    return render(request, 'service_booking.html', context)
