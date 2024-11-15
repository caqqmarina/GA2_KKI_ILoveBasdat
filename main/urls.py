from django.urls import path
from django.views.generic import TemplateView
from main import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('homepage/', views.homepage, name='homepage'),
    path('login/', views.login_view, name='login'),
    path('register_landing/', views.register_landing, name='register_landing'),
    path('register/user/', views.register_user, name='register_user'),
    path('register/worker/', views.register_worker, name='register_worker'),
]