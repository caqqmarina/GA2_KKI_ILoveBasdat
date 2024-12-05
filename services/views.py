from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import TestimonialForm
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
import psycopg2

def get_subcategories(request, category_id):
    try:
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, name FROM services_subcategory WHERE category_id = %s", (category_id,))
                subcategories = cursor.fetchall()
                subcategory_list = [{'id': subcategory[0], 'name': subcategory[1]} for subcategory in subcategories]
        return JsonResponse(subcategory_list, safe=False)
    except Exception as e:
        print(f"Error fetching subcategories: {e}")
        return JsonResponse([], safe=False)

def authenticate(request):
    user_phone = request.session.get('user_phone')

    if not user_phone:
        messages.error(request, "You need to log in first.")
        return None, False

    try:
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM main_user WHERE phone_number = %s", (user_phone,))
                user = cursor.fetchone()
                if not user:
                    messages.error(request, "User not found.")
                    return None, False

                cursor.execute("SELECT EXISTS(SELECT 1 FROM main_worker WHERE user_ptr_id = %s)", (user[0],))
                is_worker = cursor.fetchone()[0]
                return user, is_worker
            
    except Exception as e:
        print(f"Authentication error: {e}")
        messages.error(request, "An error occurred during authentication.")
        return None, False

def subcategory(request, subcategory_id=None):
    user, is_worker = authenticate(request)
    if not user:
        return redirect('login')

    try:
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                # Fetch subcategory data
                cursor.execute("""
                    SELECT id, name, description, category_id 
                    FROM services_subcategory 
                    WHERE id = %s
                """, (subcategory_id,))
                subcategory = cursor.fetchone()
                
                if not subcategory:
                    messages.error(request, "Subcategory not found.")
                    return redirect('services:service_order_list')

                # Fetch related sessions
                cursor.execute("""
                    SELECT id, session, price 
                    FROM services_servicesession 
                    WHERE subcategory_id = %s
                """, (subcategory_id,))
                sessions = cursor.fetchall()

                # Handle POST request for booking
                if request.method == 'POST' and 'book_service' in request.POST:
                    session_id = request.POST.get('session_id')
                    if session_id:
                        # Get session price from fetched sessions
                        session_price = next(
                            (session[2] for session in sessions if str(session[0]) == session_id),
                            None
                        )
                        
                        if session_price:
                            # Create worker service order
                            cursor.execute("""
                                INSERT INTO services_workerserviceorder 
                                (subcategory_id, session, price, status)
                                VALUES (%s, %s, %s, 'looking_for_worker')
                                RETURNING id
                            """, (subcategory_id, session_id, session_price))
                            conn.commit()

                            # Store in session
                            booked_sessions = request.session.get('booked_sessions', [])
                            if session_id not in booked_sessions:
                                booked_sessions.append(session_id)
                                request.session['booked_sessions'] = booked_sessions
                                request.session.modified = True
                            
                            return redirect('services:testimonials', subcategory_id=subcategory_id)

                # Fetch payment methods
                cursor.execute("SELECT user_ptr_id, bank_name FROM main_worker")
                payment_methods = dict(cursor.fetchall())

    except Exception as e:
        print(f"Error handling subcategory: {e}")
        messages.error(request, 'An error occurred while handling the subcategory.')
        return redirect('homepage')

    context = {
        'subcategory': {
            'id': subcategory[0],
            'name': subcategory[1],
            'description': subcategory[2],
            'category_id': subcategory[3],
            'user_name': user[1],
        },
        'sessions': [{'id': session[0], 'session': session[1], 'price': session[2]} for session in sessions],
        'payment_methods': payment_methods,
        'user': user,
        'is_worker': is_worker,
        'user_name': user[1] 
    }
    return render(request, 'subcategory.html', context)

@login_required
def create_testimonial(request, subcategory_id):
    if request.method == 'POST':
        form = TestimonialForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user_phone = request.session.get('user_phone')
            try:
                with psycopg2.connect(
                    dbname=settings.DATABASES['default']['NAME'],
                    user=settings.DATABASES['default']['USER'],
                    password=settings.DATABASES['default']['PASSWORD'],
                    host=settings.DATABASES['default']['HOST'],
                    port=settings.DATABASES['default']['PORT']
                ) as conn:
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT id FROM main_user WHERE phone_number = %s", (user_phone,))
                        user_id = cursor.fetchone()[0]
                        cursor.execute("""
                            INSERT INTO services_testimonial (content, subcategory_id, user_id, created_at, rating)
                            VALUES (%s, %s, %s, NOW(), %s)
                        """, (data['content'], subcategory_id, user_id, data['rating']))
                        conn.commit()
                return redirect('services:testimonials', subcategory_id=subcategory_id)
            except Exception as e:
                print(f"Error creating testimonial: {e}")
                messages.error(request, 'An error occurred while creating the testimonial.')
    else:
        form = TestimonialForm()
    return render(request, 'create_testimonial.html', {'form': form, 'subcategory_id': subcategory_id})

def testimonials(request, subcategory_id):
    try:
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM services_testimonial WHERE subcategory_id = %s ORDER BY created_at DESC", (subcategory_id,))
                testimonials = cursor.fetchall()
        return render(request, 'subcategory_detail.html', {'subcategory_id': subcategory_id, 'testimonials': testimonials})
    except Exception as e:
        print(f"Error fetching testimonials: {e}")
        messages.error(request, 'An error occurred while fetching testimonials.')
        return redirect('services:category_services', subcategory_id=subcategory_id)

def service_bookings(request):
    user, is_worker = authenticate(request)
    if not user:  # Redirect to login if user is not authenticated
        return redirect('login')
    
    try:
        # Establish database connection
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:

                cursor.execute("SELECT name FROM main_user WHERE id = %s", (user[0],))
                user_name = cursor.fetchone()[0]
                # Fetch all available sessions from the database
                cursor.execute("SELECT id, session, price, subcategory_id FROM services_servicesession")
                sessions = cursor.fetchall()

                if request.method == "POST":
                    session_id = request.POST.get('session_id')
                    subcategory_id = request.POST.get('subcategory_id')

                    if not session_id:
                        messages.error(request, "No session selected.")
                        return redirect('services:category_services', subcategory_id=subcategory_id)

                    # Initialize session variable for booked sessions if not already present
                    if 'booked_sessions' not in request.session:
                        request.session['booked_sessions'] = []

                    # Add session_id to booked_sessions list if not already added
                    if session_id not in request.session['booked_sessions']:
                        request.session['booked_sessions'].append(session_id)
                        request.session.modified = True

                    # Store subcategory_id in session for future use
                    request.session['subcategory_id'] = subcategory_id
                    
                    # Redirect to service bookings page
                    return redirect('services:service_bookings')

                # Get the booked sessions' IDs from the session
                booked_session_ids = request.session.get('booked_sessions', [])
                
                if booked_session_ids:
                    # Retrieve booked sessions based on stored session IDs
                    cursor.execute("SELECT id, session, price, subcategory_id FROM services_servicesession WHERE id IN %s", (tuple(booked_session_ids),))
                    booked_sessions = cursor.fetchall()
                else:
                    booked_sessions = []

                # Get unique subcategories from the booked sessions
                unique_subcategories = {session[3] for session in booked_sessions}  # Subcategory ID is the 4th column (index 3)

        context = {
            'user_name': user,
            'is_worker': is_worker,
            'booked_sessions': booked_sessions,
            'unique_subcategories': unique_subcategories,
            'user_name': user_name,
        }
        
        # Render the page with the context
        return render(request, 'service_booking.html', context)
    
    except Exception as e:
        print(f"Error handling service bookings: {e}")
        messages.error(request, 'An error occurred while handling service bookings.')
        return redirect('services:category_services', subcategory_id=subcategory_id)

def service_order_list(request):
    user, is_worker = authenticate(request)
    if not user or not is_worker:
        return redirect('login')

    try:
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                # First get the user's name
                cursor.execute("SELECT name FROM main_user WHERE id = %s", (user[0],))
                user_name = cursor.fetchone()[0]

                cursor.execute("SELECT * FROM main_worker WHERE user_ptr_id = %s", (user[0],))
                worker = cursor.fetchone()

                cursor.execute("SELECT * FROM services_servicecategory")
                categories = cursor.fetchall()

                cursor.execute("""
                    SELECT * FROM services_workerserviceorder
                    WHERE status = 'looking_for_worker'
                    AND subcategory_id IN (
                        SELECT subcategory_id FROM services_workerservice
                        WHERE worker_id = %s
                    )
                """, (worker[0],))
                orders = cursor.fetchall()

        context = {
            'orders': orders,
            'categories': categories,
            'user': user,
            'is_worker': is_worker,
            'user_name': user_name,
        }
        return render(request, 'service_orders/order_list.html', context)
    except Exception as e:
        print(f"Error fetching service orders: {e}")
        messages.error(request, 'An error occurred while fetching service orders.')
        return redirect('services:service_order_list')

def update_status(request, order_id):
    user, is_worker = authenticate(request)
    if not user:
        return redirect('login')

    try:
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                if is_worker:
                    cursor.execute("SELECT * FROM services_workerserviceorder WHERE id = %s", (order_id,))
                    order = cursor.fetchone()

                    if not order:
                        messages.error(request, "Order not found")
                        return redirect('services:service_order_list')

                    if order[4] == 'looking_for_worker':
                        cursor.execute("""
                            UPDATE services_workerserviceorder
                            SET status = 'worker_assigned', assigned_worker_id = %s
                            WHERE id = %s
                        """, (user[0], order_id))
                    elif order[4] == 'worker_assigned':
                        cursor.execute("""
                            UPDATE services_workerserviceorder
                            SET status = 'in_progress'
                            WHERE id = %s
                        """, (order_id,))
                    elif order[4] == 'in_progress':
                        cursor.execute("""
                            UPDATE services_workerserviceorder
                            SET status = 'completed'
                            WHERE id = %s
                        """, (order_id,))
                else:
                    cursor.execute("SELECT * FROM services_serviceorder WHERE id = %s", (order_id,))
                    order = cursor.fetchone()

                    if not order:
                        messages.error(request, "Order not found")
                        return redirect('services:service_order_list')

                    if order[2] == 'waiting_for_departure':
                        cursor.execute("""
                            UPDATE services_serviceorder
                            SET status = 'arrived_at_location'
                            WHERE id = %s
                        """, (order_id,))
                    elif order[2] == 'arrived_at_location':
                        cursor.execute("""
                            UPDATE services_serviceorder
                            SET status = 'service_in_progress'
                            WHERE id = %s
                        """, (order_id,))

                conn.commit()
                return redirect('services:service_order_list')
    except Exception as e:
        print(f"Update status error: {e}")
        messages.error(request, 'An error occurred while updating the order status.')
        return redirect('services:service_order_list')