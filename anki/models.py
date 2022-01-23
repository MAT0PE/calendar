from django.db import models

class Vocabulary(models.Model):
    foreign = models.TextField(default='')
    japanese = models.TextField(default='')
    sentence = models.TextField(blank=True)
    state = models.IntegerField(default=0)
    date = models.DateField(null=True)
    user = models.IntegerField(null=True) # user.pkを保持
    def __str__(self):
        return self.foreign
