from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Route(models.Model):
    name = models.CharField(max_length=100, unique=True)
    plant = models.ForeignKey("plants.Plant", on_delete=models.CASCADE, related_name="routes",null=True, blank=True) 
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
    SOURCE_CHOICES = [
        ('on_farm_tank', 'On-Farm Tank'),
        ('bulk_cooler', 'Bulk Cooler'),
        ('can_collection', 'Can Collection'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_transit', 'In Transit'),
        ('completed', 'Completed'),
    ]

    vehicle = models.ForeignKey(
        'Vehicle',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='transfers'
    )

    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_CHOICES,
        null=True,
        blank=True
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

    destination = models.ForeignKey(
    'plants.Plant', 
    on_delete=models.SET_NULL, 
    blank=True, 
    null=True,
    related_name='transfers_as_destination'
    )

    transfer_date = models.DateTimeField(auto_now_add=True)
    arrival_datetime = models.DateTimeField(null=True, blank=True)

    departure_weight_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight of milk (in kg) while leaving the cooperative/source."
    )

    arrival_weight_kg = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weight of milk (in kg) while arriving at the destination."
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    total_volume = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)

    emptied_at = models.DateTimeField(null=True, blank=True)

    silo = models.ForeignKey(
        'plants.Silo',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='incoming_transfers',
        help_text="The silo this milk is being transferred into."
    )


    def clean(self):
        sources = [self.bulk_cooler, self.on_farm_tank, self.can_collection]
        if sum(1 for s in sources if s is not None) > 1:
            raise ValidationError("Milk transfer can have only one source location.")

        if self.source_type == 'bulk_cooler' and not self.bulk_cooler:
            raise ValidationError("Source type is Bulk Cooler but no Bulk Cooler is set.")
        if self.source_type == 'on_farm_tank' and not self.on_farm_tank:
            raise ValidationError("Source type is On-Farm Tank but no On-Farm Tank is set.")
        if self.source_type == 'can_collection' and not self.can_collection:
            raise ValidationError("Source type is Can Collection but no Can Collection is set.")
        
        if self.silo and self.total_volume is not None:
            available_space = self.silo.capacity_liters - self.silo.current_volume

        if self.total_volume is not None and self.total_volume <= 0:
            raise ValidationError("Transfer volume must be greater than zero.")

        if self.silo and self.total_volume is not None:
            available_space = self.silo.capacity_liters - self.silo.current_volume
            if self.total_volume > available_space:
                raise ValidationError(
                    f"Cannot transfer {self.total_volume}L into silo '{self.silo.name}'. "
                    f"Available space: {available_space}L. "
                    f"Current volume: {self.silo.current_volume}L / {self.silo.capacity_liters}L."
                )

    
    def save(self, *args, **kwargs):
        if not self.pk and self.total_volume is None:
            self.total_volume = self.calculate_total_volume(save=False)

        self.full_clean()
        super().save(*args, **kwargs)

        if self.status == 'completed' and self.silo:
            self.silo.update_current_volume()

    def calculate_total_volume(self, save=True):
        if self.bulk_cooler:
            self.total_volume = self.bulk_cooler.current_volume_liters
        elif self.on_farm_tank:
            self.total_volume = self.on_farm_tank.current_volume_liters
        elif self.can_collection:
            self.total_volume = self.can_collection.total_volume_liters
        else:
            self.total_volume = 0
        if save and self.pk:  
            super().save(update_fields=['total_volume'])
        return self.total_volume

    def __str__(self):
        source = self.bulk_cooler or self.on_farm_tank or self.can_collection or "Unknown Source"
        return f"Transfer {self.id} {source.name} → {self.transfer_date}"
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['on_farm_tank'],
                name='unique_transfer_per_on_farm_tank',
                condition=models.Q(on_farm_tank__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['bulk_cooler'],
                name='unique_transfer_per_bulk_cooler',
                condition=models.Q(bulk_cooler__isnull=False)
            ),
            models.UniqueConstraint(
                fields=['can_collection'],
                name='unique_transfer_per_can_collection',
                condition=models.Q(can_collection__isnull=False)
            ),
        ]