from django.urls import path
from django.views.generic import TemplateView
from main import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('homepage/', views.homepage, name='homepage'),
    path('login/', views.login_user, name='login'),
    path('register_landing/', views.register_landing, name='register_landing'),
    path('register/user/', views.register_user, name='register_user'),
    path('register/worker/', views.register_worker, name='register_worker'),
    # path('login/', views.login_view, name='login'),
    # path('register/', views.register_view, name='register'),
    # path('logout/', views.logout_view, name='logout'),
    # path('user/profile/', views.user_profile, name='user_profile'),
    # path('worker/profile/', views.worker_profile, name='worker_profile'),
    path('logout/', views.logout_user, name='logout'),
    path('discount/', views.discount_page, name='discount'),
    path('profile/', views.profile_view, name='profile'),
    path('buy_voucher/<int:voucher_id>', views.buy_voucher, name="buy_voucher"),
    path('mypay/', views.mypay, name='mypay'),
    path('profile/<int:worker_id>', views.worker_profile, name='worker_profile'),
    path('validate_discount/', views.validate_discount, name="validate_discount" )
]
