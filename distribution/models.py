from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

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
    vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfers'
    )
    transfer_date = models.DateField(auto_now_add=True)
    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='route_milk_transfers'
    )

    bulk_cooler = models.ForeignKey(
        'collection_center.BulkCooler',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='milk_transfers'
    )
    on_farm_tank = models.ForeignKey(
        'suppliers.OnFarmTank',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='milk_transfers'
    )
    can_collection = models.ForeignKey(
        'suppliers.CanCollection',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='milk_transfers'
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

    def clean(self):
       
        sources = [self.bulk_cooler, self.on_farm_tank, self.can_collection]
        if sum(1 for s in sources if s is not None) > 1:
            raise ValidationError("Milk transfer can have only one source location.")

    def __str__(self):
        source = self.bulk_cooler or self.on_farm_tank or self.can_collection
        return f"Transfer #{self.id} from {source} – {self.transfer_date}"

    def calculate_total_volume(self):
        if self.bulk_cooler:
            self.total_volume = self.bulk_cooler.current_volume_liters
        elif self.on_farm_tank:
            self.total_volume = self.on_farm_tank.current_volume_liters
        elif self.can_collection:
            self.total_volume = self.can_collection.total_volume_liters
        else:
            self.total_volume = 0
        self.save(update_fields=['total_volume'])
        return self.total_volume
