from django.urls import path
from . import views

urlpatterns = [
    path('check_answer', views.check_answer, name='check_answer'),
    path('vocabulary', views.vocabulary, name='vocabulary'),
    path('type_in_foreign', views.type_in_foreign, name='type_in_foreign'),
    path('register_vocab', views.register_vocab, name='register_vocab'),
    path('verification', views.verification, name='verification'),
]