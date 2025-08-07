from django.db import models
from django.contrib.auth.models import User

class Route(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name


class Distributor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    address = models.TextField()
    license_number = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"({self.user.username if self.user else 'No user'})"

class Vehicle(models.Model):
    distributor = models.ForeignKey(
        'Distributor',
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    name = models.CharField(max_length=100)
    vehicle_id = models.CharField(max_length=50, unique=True)
    capacity_liters = models.FloatField(null=True, blank=True) 
    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehicles'
    )

    @property
    def is_available(self):
        return not self.transfers.filter(status__in=['scheduled', 'in_transit']).exists()

    def __str__(self):
        return f"{self.name} ({self.vehicle_id})"
    
class MilkTransfer(models.Model):
    distributor = models.ForeignKey(
        Distributor,
        on_delete=models.CASCADE,
        related_name='transfers'
    )
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfers'
    )
    milk_transfer = models.ForeignKey(
        'suppliers.MilkLot',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='milk_lots'
    )
    transfer_date = models.DateField(auto_now_add=True)
    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfers'
    )
    status_choices = [
        ('scheduled', 'Scheduled'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
    ]
    status = models.CharField(
        max_length=20,
        choices=status_choices,
        default='scheduled'
    )
    total_volume = models.FloatField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Transfer #{self.id} – {self.vehicle} – {self.transfer_date}"

    def calculate_total_volume(self):
        self.total_volume = sum(lot.volume_l for lot in self.milk_lots.all())
        return self.total_volume
