# main/urls.py
from django.contrib import admin
from django.urls import path
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.landing_page, name='landing'),
    path('homepage/', views.homepage, name='homepage'),  # Separate URL for homepage
    path('login/', views.login_view, name='login'),
    path('register_landing/', views.register_landing, name='register_landing'),
    path('register/user/', views.register_user, name='register_user'),
    path('register/worker/', views.register_worker, name='register_worker'),
    # path('login/', views.login_view, name='login'),
    # path('register/', views.register_view, name='register'),
    # path('logout/', views.logout_view, name='logout'),

]

