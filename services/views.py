from django.shortcuts import render, get_object_or_404, redirect
from services.models import Subcategory, Worker, Testimonial, ServiceSession, ServiceCategory
from services.forms import SubcategoryForm, CategoryForm
from django.contrib.auth.decorators import login_required
from .forms import TestimonialForm

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
