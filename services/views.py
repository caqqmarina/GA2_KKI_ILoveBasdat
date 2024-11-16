from django.shortcuts import render, get_object_or_404
from .models import Subcategory, Worker, Testimonial, ServiceSession

def show_page(request, subcategory_id):
    # Retrieve the subcategory using the provided ID
    subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    
    # Retrieve workers, testimonials, and sessions related to this subcategory
    workers = Worker.objects.filter(services__subcategory=subcategory)
    testimonials = Testimonial.objects.filter(subcategory=subcategory)
    sessions = ServiceSession.objects.filter(subcategory=subcategory)
    
    # Render the template with context data
    return render(request, 'subcategory.html', {
        'subcategory': subcategory,
        'workers': workers,
        'testimonials': testimonials,
        'sessions': sessions,
    })

def list_services(request):
    subcategories = Subcategory.objects.all()
    return render(request, 'list_services.html', {'subcategories': subcategories})
