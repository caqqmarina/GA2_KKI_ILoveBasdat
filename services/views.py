from django.shortcuts import render, get_object_or_404, redirect
from services.models import Subcategory, Worker, Testimonial, ServiceSession, ServiceCategory
from services.forms import SubcategoryForm, CategoryForm
from django.contrib.auth.decorators import login_required
from .forms import TestimonialForm
from django.contrib import messages
from .models import User, Worker, ServiceOrder

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

@login_required
def create_testimonial(request, subcategory_id):
    subcategory = Subcategory.objects.get(id=subcategory_id)
    if request.method == 'POST':
        form = TestimonialForm(request.POST)
        if form.is_valid():
            testimonial = form.save(commit=False)
            testimonial.user = request.user
            testimonial.subcategory = subcategory
            testimonial.save()
            return redirect('subcategory_detail', subcategory_id=subcategory.id)  # Redirect to subcategory detail page
    else:
        form = TestimonialForm()
    return render(request, 'create_testimonial.html', {'form': form, 'subcategory': subcategory})

def testimonials(request, subcategory_id):
    subcategory = Subcategory.objects.get(id=subcategory_id)
    testimonials = Testimonial.objects.filter(subcategory=subcategory).order_by('-date')
    return render(request, 'subcategory_detail.html', {'subcategory': subcategory, 'testimonials': testimonials})

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

def service_order_list(request):
    user, is_worker = authenticate(request)

    if not user:  # Redirect to login if user is not authenticated
        return redirect('login')

    # Display a list of all service orders
    orders = ServiceOrder.objects.all()

    context = {
        'orders': orders,
        'user': user,
        'is_worker': is_worker
    }

    return render(request, 'service_orders/order_list.html', context)

def update_status(request, order_id):
    order = ServiceOrder.objects.get(id=order_id)

    # Update the order status based on the current status
    if order.status == 'waiting_for_departure':
        order.status = 'arrived_at_location'
    elif order.status == 'arrived_at_location':
        order.status = 'service_in_progress'
    elif order.status == 'service_in_progress':
        order.status = 'order_completed'
    elif order.status == 'order_completed' or order.status == 'order_canceled':
        # No further status changes are allowed after completion or cancellation
        return redirect('service_order_list')

    order.save()
    return redirect('service_order_list')

