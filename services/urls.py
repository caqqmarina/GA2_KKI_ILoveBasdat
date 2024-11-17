from django.urls import path
from services.views import subcategory
from . import views

app_name = 'services'

urlpatterns = [
    path('<int:subcategory_id>/', subcategory, name='category_services'),
    path('subcategory/<int:subcategory_id>/testimonials/', views.testimonials, name='testimonials'),
    path('subcategory/<int:subcategory_id>/create-testimonial/', views.create_testimonial, name='create_testimonial'),
]