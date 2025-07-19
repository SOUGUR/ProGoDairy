from django.db import models
from django.contrib.auth.models import User
import uuid

class DairyPlant(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    location = models.TextField()
    contact_email = models.EmailField(unique=True)
    contact_phone = models.CharField(max_length=15, blank=True)
    milk_rate = models.FloatField(default=0.50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class PlantEmployee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employee_profile')
    plant = models.ForeignKey(DairyPlant, on_delete=models.CASCADE, related_name='employees')
    role = models.CharField(max_length=100, choices=[
        ('TESTER', 'Milk Tester'),
        ('MANAGER', 'Plant Manager'),
        ('INVENTORY', 'Inventory Manager'),
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['user__username']

    def __str__(self):
        return f"{self.user.username} ({self.role}) at {self.plant.name}"
