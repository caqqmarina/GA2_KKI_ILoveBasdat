from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import TestimonialForm, ServiceJobForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
from django.db import connection
import psycopg2
import json

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
                if category_id:
                    cursor.execute("SELECT id, name FROM services_subcategory WHERE category_id = %s", (category_id,))
                else:
                    cursor.execute("SELECT id, name FROM services_subcategory")
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
                # Check if user exists
                cursor.execute("SELECT * FROM main_user WHERE phone_number = %s", (user_phone,))
                user = cursor.fetchone()
                
                if not user:
                    messages.error(request, "User not found.")
                    return None, False
                
                # Check if user is a worker
                cursor.execute("SELECT EXISTS(SELECT 1 FROM main_worker WHERE user_ptr_id = %s)", (user[0],))
                is_worker = cursor.fetchone()[0]
                return user, is_worker
                
    except Exception as e:
        print(f"Authentication error: {e}")
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
                    SELECT s.id, s.name, s.description, s.category_id, c.name AS category_name 
                    FROM services_subcategory s
                    INNER JOIN services_servicecategory c ON s.category_id = c.id
                    WHERE s.id = %s
                """, (subcategory_id,))
                subcategory = cursor.fetchone()
                
                if not subcategory:
                    messages.error(request, "Subcategory not found.")
                    return redirect('services:service_order_list')
                
                cursor.execute("""
                    SELECT w.id AS worker_id, w.name
                    FROM main_user w
                    INNER JOIN workers_category wc ON w.id = wc.worker_id
                    WHERE wc.category_id = %s
                """, (subcategory[3],))
                workers = cursor.fetchall()
                workers_list = [{'worker_id': w[0], 'name': w[1]} for w in workers]

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

                # Check if the worker is already in the category
                cursor.execute("""
                    SELECT 1 FROM workers_category 
                    WHERE worker_id = %s AND category_id = %s
                """, (user[0], subcategory[3],))
                is_joined = cursor.fetchone()

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
            'category_name' : subcategory[4],
            'user_name' : user[1],
        },
        'join_button': not is_joined,
        'workers': workers_list,
        'sessions': [{'id': session[0], 'session': session[1], 'price': session[2]} for session in sessions],
        'payment_methods': payment_methods,
        'user': user,
        'is_worker': is_worker,
        'user_name' : user[1]
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
                    final_price = request.POST.get('final_price')

                    if not session_id:
                        messages.error(request, "No session selected.")
                        return redirect('services:category_services', subcategory_id=subcategory_id)

                    # Retrieve the session details for the current session being booked
                    cursor.execute("""
                        SELECT 
                            s.id AS session_id, 
                            s.session AS session_name, 
                            s.price, 
                            sc.id AS subcategory_id, 
                            sc.name AS subcategory_name
                        FROM 
                            services_servicesession s
                        INNER JOIN 
                            services_subcategory sc ON s.subcategory_id = sc.id
                        WHERE 
                            s.id = %s
                    """, (session_id,))
                    booked_session = cursor.fetchone()  # Get the details of the current session being booked

                    # Check if the session has already been booked by the current user
                    cursor.execute("""
                        SELECT id FROM public.booked_sessions 
                        WHERE session_id = %s AND user_id = %s
                    """, (booked_session[0], user[0]))
                    existing_booking = cursor.fetchone()

                    if not existing_booking:
                        # Insert the session into the booked_sessions table if not already present
                        cursor.execute("""
                            INSERT INTO public.booked_sessions (session_id, session_name, price, subcategory_id, subcategory_name, worker_name, action, user_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            booked_session[0],  # session_id
                            booked_session[1],  # session_name
                            final_price,  # price
                            booked_session[3],  # subcategory_id
                            booked_session[4],  # subcategory_name
                            '',  # worker_name (replace with actual worker name if available)
                            'None',            # action (can be updated later)
                            user[0]            # user_id
                        ))
                        conn.commit()

                    # Redirect to service bookings page after successful booking
                    return redirect('services:service_bookings')
                
                cursor.execute("""
                    SELECT 
                        s.id AS session_id, 
                        s.session AS session_name, 
                        bs.price, 
                        sc.id AS subcategory_id, 
                        sc.name AS subcategory_name,
                        bs.worker_name AS worker_name,
                        bs.status AS status,
                        bs.id AS id
                    FROM 
                        public.booked_sessions bs
                    INNER JOIN 
                        services_servicesession s ON bs.session_id = s.id
                    INNER JOIN 
                        services_subcategory sc ON s.subcategory_id = sc.id
                    WHERE 
                        bs.user_id = %s
                """, (user[0],))  # 'user[0]' is the user_id from the authenticated user
                booked_sessions = cursor.fetchall()

                # If there are no booked sessions, set an empty list
                if not booked_sessions:
                    booked_sessions = []

                booked_sessions_data = [
                    {'session_id': session[0], 'session': session[1], 'price': session[2], 'subcategory_id': session[3], 'subcategory_name': session[4], 'worker_name': session[5],
                     'status': session[6], 'id': session[7]}
                    for session in booked_sessions
                ]

                # Get unique subcategories from the booked sessions
                unique_subcategories = {session[4] for session in booked_sessions}  # Subcategory name is at index 4
        
        context = {
            'user_name': user_name,
            'is_worker': is_worker,
            'booked_sessions': booked_sessions_data,
            'unique_subcategories': unique_subcategories,
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
    
def service_status(request):
    status_filter = request.GET.get('status', None)
    name_filter = request.GET.get('name', None)

    query = "SELECT * FROM service_orders WHERE 1=1"
    params = []

    if status_filter:
        query += " AND status = %s"
        params.append(status_filter)

    if name_filter:
        query += " AND order_name LIKE %s"
        params.append(f"%{name_filter}%")

    with connection.cursor() as cursor:
        cursor.execute(query, params)
        columns = [col[0] for col in cursor.description]
        orders = [dict(zip(columns, row)) for row in cursor.fetchall()]

    return render(request, 'service_status.html', {'orders': orders})

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
                    # Worker-related order handling
                    cursor.execute("SELECT id, status FROM services_workerserviceorder WHERE id = %s", (order_id,))
                    order = cursor.fetchone()

                    if not order:
                        messages.error(request, "Order not found.")
                        return redirect('services:service_order_list')

                    current_status = order[1]
                    worker_status_updates = {
                        'looking_for_worker': ('worker_assigned', "assigned_worker_id"),
                        'worker_assigned': ('in_progress', None),
                        'in_progress': ('completed', None),
                    }

                    if current_status in worker_status_updates:
                        next_status, extra_field = worker_status_updates[current_status]
                        update_query = f"""
                            UPDATE services_workerserviceorder
                            SET status = %s {', ' + extra_field + ' = %s' if extra_field else ''}
                            WHERE id = %s
                        """
                        params = [next_status]
                        if extra_field:
                            params.append(user[0])  # Assuming user[0] is the worker's ID
                        params.append(order_id)

                        cursor.execute(update_query, params)
                else:
                    # Non-worker-related order handling
                    cursor.execute("SELECT id, status FROM services_serviceorder WHERE id = %s", (order_id,))
                    order = cursor.fetchone()

                    if not order:
                        messages.error(request, "Order not found.")
                        return redirect('services:service_order_list')

                    current_status = order[1]
                    customer_status_updates = {
                        'waiting_for_departure': 'arrived_at_location',
                        'arrived_at_location': 'service_in_progress',
                    }

                    if current_status in customer_status_updates:
                        next_status = customer_status_updates[current_status]
                        cursor.execute("""
                            UPDATE services_serviceorder
                            SET status = %s
                            WHERE id = %s
                        """, (next_status, order_id))

                conn.commit()
                messages.success(request, "Order status updated successfully.")
                return redirect('services:service_order_list')

    except Exception as e:
        print(f"Update status error: {e}")
        messages.error(request, 'An error occurred while updating the order status.')
        return redirect('services:service_order_list')

def service_job(request):
    if request.method == "GET":
        # Fetch categories and subcategories from the database
        try:
            with psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            ) as conn:
                with conn.cursor() as cursor:
                    # Fetch categories
                    cursor.execute("SELECT id, name FROM services_servicecategory")
                    categories = [(cat[0], cat[1]) for cat in cursor.fetchall()]

                    # Fetch subcategories
                    cursor.execute("SELECT id, name, category_id FROM services_subcategory")
                    subcategories = cursor.fetchall()

        except Exception as e:
            print(f"Error fetching categories/subcategories: {e}")
            messages.error(request, "An error occurred while loading the form.")
            return redirect('homepage')

        # Render form with fetched data
        form = ServiceJobForm(
            category_choices=categories,
            subcategory_choices=[(sub[0], sub[1]) for sub in subcategories]
        )
        return render(request, 'service_job_form.html', {'form': form})

    elif request.method == "POST":
        # Process the form submission
        form = ServiceJobForm(request.POST)
        if form.is_valid():
            category_id = form.cleaned_data['category']
            subcategory_id = form.cleaned_data['subcategory']

            try:
                # Perform operations like assigning a worker to the job
                with psycopg2.connect(
                    dbname=settings.DATABASES['default']['NAME'],
                    user=settings.DATABASES['default']['USER'],
                    password=settings.DATABASES['default']['PASSWORD'],
                    host=settings.DATABASES['default']['HOST'],
                    port=settings.DATABASES['default']['PORT']
                ) as conn:
                    with conn.cursor() as cursor:
                        # Assign the worker or create the job record
                        cursor.execute("""
                            INSERT INTO services_workerserviceorder (subcategory_id, status)
                            VALUES (%s, 'looking_for_worker')
                        """, (subcategory_id,))
                        conn.commit()

                messages.success(request, "Service job created successfully!")
                return redirect('service_order_list')  # Redirect to order list or another relevant page
            except Exception as e:
                print(f"Error creating service job: {e}")
                messages.error(request, "An error occurred while creating the job.")
                return redirect('service_job')

        else:
            messages.error(request, "Invalid input. Please check the form.")
            return render(request, 'service_job_form.html', {'form': form})

def service_job_status(request):
    # Fetch orders for the worker (assuming worker_id = 1)
    try:
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM service_orders WHERE worker_id = %s", (1,))  # Assuming worker_id = 1
                orders = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return redirect('homepage')

    # Handle status updates
    if request.method == "POST" and "order_id" in request.POST and "action" in request.POST:
        order_id = request.POST.get("order_id")
        action = request.POST.get("action")

        try:
            with psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            ) as conn:
                with conn.cursor() as cursor:
                    # Workflow of updating status
                    if action == "arrive":
                        cursor.execute("""
                            UPDATE service_orders
                            SET status = 'Worker Arrived at Location'
                            WHERE id = %s AND status = 'Waiting for Worker to Depart'
                        """, (order_id,))
                    elif action == "start_service":
                        cursor.execute("""
                            UPDATE service_orders
                            SET status = 'Service in Progress'
                            WHERE id = %s AND status = 'Worker Arrived at Location'
                        """, (order_id,))
                    elif action == "complete":
                        cursor.execute("""
                            UPDATE service_orders
                            SET status = 'Order Completed'
                            WHERE id = %s AND status = 'Service in Progress'
                        """, (order_id,))

                    conn.commit()
        except Exception as e:
            print(f"Error updating service order status: {e}")

    return render(request, "service_job_status.html", {
        "orders": orders,
    })

def join_category(request, category_id, subcategory_id):
    user, is_worker = authenticate(request)
    if not user or not is_worker:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

    try:
        with psycopg2.connect(
            dbname=settings.DATABASES['default']['NAME'],
            user=settings.DATABASES['default']['USER'],
            password=settings.DATABASES['default']['PASSWORD'],
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT']
        ) as conn:
            with conn.cursor() as cursor:
                # Check if the worker is already in the category
                cursor.execute("""
                    SELECT id FROM workers_category 
                    WHERE worker_id = %s AND category_id = %s
                """, (user[0], category_id))
                relationship = cursor.fetchone()

                if relationship:
                    # Worker is already joined, return success
                    return JsonResponse({'success': True, 'message': 'Already joined this category.'})
                
                # Add the worker to the category
                cursor.execute("""
                    INSERT INTO workers_category (worker_id, category_id)
                    VALUES (%s, %s)
                """, (user[0], category_id))
                conn.commit()

                return JsonResponse({'success': True, 'message': 'Successfully joined the category.'})

    except Exception as e:
        print(f"Error adding worker to category: {e}")
        return JsonResponse({'success': False, 'message': 'An error occurred.'}, status=500)

def cancel_order(request):
    user, is_worker = authenticate(request)
    if not user:
        return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

    if request.method == 'POST':
        try:
            # Parse the request data
            data = json.loads(request.body)
            id = data.get('id')

            if not id:
                return JsonResponse({'success': False, 'message': 'ID is required.'}, status=400)

            # Establish database connection
            with psycopg2.connect(
                dbname=settings.DATABASES['default']['NAME'],
                user=settings.DATABASES['default']['USER'],
                password=settings.DATABASES['default']['PASSWORD'],
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT']
            ) as conn:
                with conn.cursor() as cursor:
                    # Delete the session from the booked_sessions table
                    cursor.execute("""
                        UPDATE public.booked_sessions
                        SET status = %s
                        WHERE id = %s AND user_id = %s
                    """, ('Canceled', id, user[0]))

                    conn.commit()

            return JsonResponse({'success': True, 'message': 'Order cancelled successfully.'})

        except Exception as e:
            print(f"Error cancelling order: {e}")
            return JsonResponse({'success': False, 'message': 'An error occurred while cancelling the order.'}, status=500)

    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400)