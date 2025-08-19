from django.db import models
from distribution.models import Route
from django.contrib.auth.models import User

class Tester(models.Model):
    """
    Plant employee authorized to perform milk-quality tests.
    Includes extended tester-specific details.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    designation = models.CharField(max_length=100, default="Milk Quality Tester")
    routes = models.ManyToManyField(Route, related_name='testers', blank=True)

    def __str__(self):
        full_name = self.user.get_full_name()
        return f"Tester: {full_name or self.user.username} (ID: {self.employee_id})"



class Plant(models.Model):
    name = models.CharField(max_length=100, unique=True)  
    location = models.CharField(max_length=200)  
    capacity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Daily processing capacity in liters")
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    established_date = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=True, help_text="Mark inactive if plant is closed or not in use")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.location})"

