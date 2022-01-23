from django.db import models

class Message(models.Model):
    sender = models.IntegerField()
    receiver = models.IntegerField()
    time = models.DateTimeField()
    text = models.TextField()
    read = models.BooleanField(default=False)

class Request(models.Model):
    sender = models.IntegerField()#pkを保持
    receiver = models.IntegerField()#pkを保持
