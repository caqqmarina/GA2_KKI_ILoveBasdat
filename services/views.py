from django.shortcuts import render, get_object_or_404, redirect
from services.models import Subcategory, Worker, Testimonial, ServiceSession, ServiceCategory
from services.forms import SubcategoryForm, CategoryForm

def subcategory(request, subcategory_id=None):
    subcategory = get_object_or_404(Subcategory, pk=subcategory_id)
    
    # Fetch related data (workers, testimonials, service sessions)
    #workers = Worker.objects.filter(subcategory=subcategory)
    #testimonials = Testimonial.objects.filter(service_category=subcategory.category)  # Assuming testimonials are tied to the category
    sessions = subcategory.sessions.all()

    context = {
        'subcategory': subcategory,
        'category': subcategory.category,  # This includes the category info
        'sessions': sessions,
    }

    return render(request, 'subcategory.html', context)

def service_bookings(request):
    if request.method == "POST":
        return render(request, 'service_bookings.html')
