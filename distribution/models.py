from django.db import models
import uuid
from milk.models import MilkLot

class Distributor(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    contact_email = models.EmailField(unique=True)
    contact_phone = models.CharField(max_length=15, blank=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Distribution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    milk_lot = models.ForeignKey(MilkLot, on_delete=models.CASCADE, related_name='distributions')
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE, related_name='distributions')
    volume_assigned = models.FloatField()
    distribution_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['distribution_date']

    def __str__(self):
        return f"Distribution of {self.volume_assigned}L from Lot {self.milk_lot.lot_number} to {self.distributor.name}"

    def validate_volume(self):
        if self.volume_assigned > self.milk_lot.volume:
            raise ValueError("Assigned volume exceeds lot volume.")
        self.milk_lot.volume -= self.volume_assigned
        self.milk_lot.save()
