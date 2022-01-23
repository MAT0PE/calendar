from django.urls import path
from . import views

urlpatterns = [
    path('', views.main, name='main'),
    path('register_record', views.register_record, name='register_record'),
    path('detail', views.detail, name='detail'),
    path('first_settings', views.first_settings, name='first_settings'),
    path('edit_and_delete', views.edit_and_delete, name='edit_and_delete'),
    path('edit/<int:record_pk>', views.edit, name='edit'),
    path('delete/<int:record_pk>', views.delete, name='delete'),
    path('not_allowed', views.not_allowed, name='not_allowed'),
]