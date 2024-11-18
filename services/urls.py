from django.urls import path
from . import views
from services.views import (
    subcategory,
    service_bookings,
    testimonials,
    create_testimonial,
    service_order_list, 
    update_status
)

app_name = 'services'

urlpatterns = [
    path('<int:subcategory_id>/', subcategory, name='category_services'),
    path('subcategory/<int:subcategory_id>/testimonials/', testimonials, name='testimonials'),
    path('subcategory/<int:subcategory_id>/create-testimonial/', create_testimonial, name='create_testimonial'),
    path('bookings/', service_bookings, name='service_bookings'),
    path('', service_order_list, name='service_order_list'),
    path('update_status/<int:order_id>/', update_status, name='update_status'),
]
