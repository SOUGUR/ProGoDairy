from django.db import models
from suppliers.models import MilkLot
from django.db.models import Q

class CompositeSample(models.Model):

    bulk_cooler  = models.ForeignKey(
        'collection_center.BulkCooler', null=True, blank=True, on_delete=models.CASCADE,
        related_name='samples'
    )
    on_farm_tank = models.ForeignKey(
        'suppliers.OnFarmTank', null=True, blank=True, on_delete=models.CASCADE,
        related_name='samples'
    )
    vehicle  = models.ForeignKey(  
        'distribution.Vehicle', null=True, blank=True, on_delete=models.CASCADE,
        related_name='samples'
    )

    sample_volume_ml = models.PositiveSmallIntegerField(default=50)  
    collected_at     = models.DateTimeField(auto_now_add=True)
    temperature_c    = models.FloatField(default=4.0)  
    received_at_lab  = models.DateTimeField(null=True, blank=True)
    remark = remark = models.TextField(null=True, blank=True)

    fat_percent        = models.FloatField(null=True, blank=True)
    snf_percent        = models.FloatField(null=True, blank=True)
    protein_percent    = models.FloatField(null=True, blank=True)
    bacterial_count    = models.PositiveIntegerField(null=True, blank=True)  
    antibiotic_residue = models.BooleanField(default=False)
    added_water_percent= models.FloatField(default=0.0)
 
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected')
    ]

    passed = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending'
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.passed == 'approved':
            self.approve_related_milk_lots()
        elif self.passed == 'rejected':
            self.reject_related_milk_lots()

    def approve_related_milk_lots(self):
        """
        Approve all MilkLots that belong to the same bulk_cooler or on_farm_tank.
        """
        if not self.bulk_cooler and not self.on_farm_tank:
            return

        query = Q()
        if self.bulk_cooler:
            query |= Q(bulk_cooler=self.bulk_cooler)
        if self.on_farm_tank:
            query |= Q(on_farm_tank=self.on_farm_tank)

        MilkLot.objects.filter(query).update(status='approved')

    def reject_related_milk_lots(self):
        """
        Optional: Reject related milk lots if sample fails.
        """
        if not self.bulk_cooler and not self.on_farm_tank:
            return

        query = Q()
        if self.bulk_cooler:
            query |= Q(bulk_cooler=self.bulk_cooler)
        if self.on_farm_tank:
            query |= Q(on_farm_tank=self.on_farm_tank)

        MilkLot.objects.filter(query).update(
            status='rejected',
            price_per_litre=0.00,
            total_price=0.00
        )

    def __str__(self):
        if self.bulk_cooler:
            return f"Sample from Bulk Cooler {self.bulk_cooler}"
        if self.on_farm_tank:
            return f"Sample from On-Farm Tank {self.on_farm_tank}"
        if self.vehicle:
            return f"Sample from Vehicle {self.vehicle}"
        return f"Composite Sample {self.id}"
    

