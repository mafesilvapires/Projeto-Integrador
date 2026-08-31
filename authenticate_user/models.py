from django.db import models
from django.contrib.auth.models import User

class PerfilTOTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret = models.CharField(max_length=32)