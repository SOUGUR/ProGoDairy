from django.contrib.auth.models import User
from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)  

    def __str__(self):
        return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roles = models.ManyToManyField(Role)

    def __str__(self):
        return f"{self.user.username}'s profile"
