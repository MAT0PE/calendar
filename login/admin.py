from django.contrib import admin
from .models import User, IdCounter

admin.site.register(User)
admin.site.register(IdCounter)