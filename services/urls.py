from django.urls import path
from . import views
from services.views import (
    subcategory,
    service_bookings,
    testimonials,
    create_testimonial,
    service_order_list,
    update_status,
    service_status,
    service_job,
    get_subcategories,
)

app_name = 'services'

urlpatterns = [
    path('<int:subcategory_id>/', subcategory, name='category_services'),
    path('subcategory/<int:subcategory_id>/testimonials/', testimonials, name='testimonials'),
    path('subcategory/<int:subcategory_id>/create-testimonial/', create_testimonial, name='create_testimonial'),
    path('bookings/', service_bookings, name='service_bookings'),
    path('service-order-list/', service_order_list, name='service_order_list'),
    path('update_status/<int:order_id>/', update_status, name='update_status'),
    path('jobs/', service_order_list, name='service_order_list'),  # Alias for `service_order_list`
    path('service-status/', service_status, name='service_status'),
    path('service-job/', service_job, name='service_job'),
    path('api/subcategories/<int:category_id>/', get_subcategories, name='get_subcategories'),
]
