from django.db import models
from distribution.models import Route
from django.contrib.auth.models import User
from distribution.models import MilkTransfer

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, related_name="employees")
    routes = models.ManyToManyField(Route, related_name="employees", blank=True)

    def __str__(self):
        full_name = self.user.get_full_name()
        return f"{self.role.name if self.role else 'Employee'}: {full_name or self.user.username} (ID: {self.employee_id})"


class Plant(models.Model):
    name = models.CharField(max_length=100, unique=True)  
    location = models.CharField(max_length=200)  
    capacity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Daily processing capacity in liters")
    contact_persons = models.ManyToManyField(
        "Employee",
        related_name="plants_as_contact",
        blank=True,
        help_text="Select one or more employees who are contact persons for this plant."
    )
    contact_number = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    established_date = models.DateField(blank=True, null=True)
    active = models.BooleanField(default=True, help_text="Mark inactive if plant is closed or not in use")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.location})"

class Silo(models.Model):
    MILK_TYPES = [
        ('raw', 'Raw Milk'),
        ('pasteurized', 'Pasteurized'),
        ('standardized', 'Standardized'),
        ('skim', 'Skim Milk'),
        ('cream', 'Cream'),
    ]

    STATUS_CHOICES = [
        ('empty', 'Empty'),
        ('filling', 'Filling'),
        ('full', 'Full'),
        ('draining', 'Draining'),
        ('cleaning', 'Cleaning'),
        ('offline', 'Offline'),
    ]

    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    code = models.CharField(max_length=20, unique=True)
    capacity_liters = models.DecimalField(max_digits=10, decimal_places=2)
    current_volume = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    
    milk_type = models.CharField(max_length=20, choices=MILK_TYPES, default='raw')
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # °C
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='empty')
    
    is_clean = models.BooleanField(default=True)
    last_cleaned_at = models.DateTimeField(null=True, blank=True)
    last_cleaned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def update_current_volume(self):
        total = MilkTransfer.objects.filter(
            silo=self,
            status='completed'
        ).aggregate(
            total_volume=models.Sum('total_volume')
        )['total_volume'] or 0

        if float(self.current_volume) != float(total):
            self.current_volume = total
            self.save(update_fields=['current_volume'])
            print(f"Silo {self.name}: Updated volume to {self.current_volume}L")
            
    def __str__(self):
        return f"{self.code} - {self.name} - {self.current_volume}/{self.capacity_liters} L"