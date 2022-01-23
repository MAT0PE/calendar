from django.urls import path
from . import views

urlpatterns = [
    path('friends', views.friends, name='friends'),
    path('chat/<slug:you>', views.chat, name='chat'),
    path('search', views.search, name='search'),
    path('requests', views.requests, name='requests'),
    path('profile', views.profile, name='my_profile'),
    path('edit_profile', views.edit_profile, name='edit_profile'),
#     path('profile/<slug:id>', views.your_profile, name='your_profile'),
]