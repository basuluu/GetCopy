from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.


class File(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.DO_NOTHING)
    url = models.URLField(null=True, blank=True, max_length=250)
    method = models.CharField(max_length=20, default="")
    file = models.FilePathField()
    ready = models.BooleanField(default=False)
