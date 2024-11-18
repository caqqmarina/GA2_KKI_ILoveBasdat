from django.urls import path
from services.views import (
    subcategory,
    service_bookings,
    testimonials,
    create_testimonial,
)

app_name = 'services'

urlpatterns = [
    path('<int:subcategory_id>/', subcategory, name='category_services'),
    path('subcategory/<int:subcategory_id>/testimonials/', testimonials, name='testimonials'),
    path('subcategory/<int:subcategory_id>/create-testimonial/', create_testimonial, name='create_testimonial'),
    path('bookings/', service_bookings, name='service_bookings'),
]
