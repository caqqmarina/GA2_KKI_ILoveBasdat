from django.urls import path
from services.views import list_services

app_name = 'services'

urlpatterns = [
    path('', list_services, name='list_services'),  # URL: /services/
]