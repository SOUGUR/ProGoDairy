from django.db import models
from django.contrib.auth.models import User
import uuid

class Supplier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supplier_profile')
    name = models.CharField(max_length=255)
    contact_email = models.EmailField(unique=True)
    contact_phone = models.CharField(max_length=15, blank=True)
    address = models.TextField()
    supply_capacity = models.FloatField(help_text="Liters per day")
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def validate_capacity(self, threshold=100.0):
        return self.supply_capacity >= threshold
