from django.urls import path
from services.views import subcategory

app_name = 'services'

urlpatterns = [
    path('<int:subcategory_id>/', subcategory, name='category_services'),
]