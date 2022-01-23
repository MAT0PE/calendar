from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinLengthValidator

class User(models.Model):
    email = models.EmailField()
    name = models.CharField(max_length=20, default='', validators=[MinLengthValidator(1)])
    friends = models.TextField(default='', blank=True)#pkをカンマで区切って保持
    password = models.CharField(max_length=20, default='', validators=[MinLengthValidator(4)])
    activated = models.BooleanField(default=False)
    userid = models.CharField(default='', max_length=9)
    message = models.CharField(default='', max_length=50, blank=True)
    ranking = models.BooleanField(default=True)

class IdCounter(models.Model):
    counter = models.IntegerField(default=1)