from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    """
    Model for user representation
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)