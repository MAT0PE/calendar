from django.conf import settings
from django.db import models
from django.utils import timezone

class Record(models.Model):
    user = models.IntegerField()#pkを保持
    start = models.DateTimeField()
    end = models.DateTimeField()
    subject = models.CharField(max_length=20)

class Day(models.Model):
    user = models.IntegerField()
    date = models.DateField()
    minutes = models.IntegerField(default=0)

class Week(models.Model):
    user = models.IntegerField()
    date = models.DateField() # この日から始まる一週間
    minutes = models.IntegerField(default=0)