from django.urls import path
from services.views import subcategory, service_bookings

app_name = 'services'

urlpatterns = [
    path('<int:subcategory_id>/', subcategory, name='category_services'),
    path('bookings/', service_bookings, name='service_bookings'),
]