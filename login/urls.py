from django.urls import path
from . import views

urlpatterns = [
    path('login', views.login, name='login'),
    path('register_mail', views.register_mail, name='register_mail'),
    path('sent_a_mail', views.sent_a_mail, name='sent_a_mail'),
    path('reset_mail', views.reset_mail, name='reset_mail'),
    path('reset/<int:pk>', views.reset, name='reset'),
    path('reset_completed', views.reset_completed, name='reset_completed'),
    path('register/<int:pk>', views.register, name='register'),
    path('logout', views.logout, name='logout'),
    path('register_completed', views.register_completed, name='register_completed'),
    path('already_registered', views.already_registered, name='already_registered'),
    path('already_used', views.already_used, name='already_used'),
]