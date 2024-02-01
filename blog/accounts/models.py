from django.db import models
from django.contrib.auth.models import User
from datetime import date

# Create your models here.


class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    upload_date = models.DateField(default=date.today)
    image = models.ImageField(upload_to='uploads/')

    class Meta:
        unique_together = ('user', 'upload_date')