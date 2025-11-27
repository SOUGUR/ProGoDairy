from django.db import models
from suppliers.models import MilkLot
from django.db.models import Q
from decimal import Decimal

class MilkPricingConfig(models.Model):
    route = models.OneToOneField("distribution.Route", on_delete=models.CASCADE, related_name="pricing_config")
    # Base values
    base_price = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal("26.00"))
    added_water_max = models.FloatField(default=3.0)

    # Bonus thresholds
    fat_min = models.FloatField(default=3.5)
    fat_bonus = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("1.50"))

    snf_min = models.FloatField(default=8.5)
    snf_bonus = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("1.00"))

    protein_min = models.FloatField(default=3.0)
    protein_bonus = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.50"))

    urea_max = models.FloatField(default=70.0)
    urea_bonus = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.50"))

    bacteria_max = models.PositiveIntegerField(default=50000)
    bacteria_bonus = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.50"))

    # Water penalty
    water_penalty_per_percent = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0.10"))

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Milk Pricing Config (Updated {self.updated_at})"


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
        related_name='gateSamples'
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
    
    sample_type = models.CharField(
        max_length=20,
        choices=[('instant-gate tests', 'Instant-Gate Tests'),
                 ('society test', 'Society Test')],
        default='society test'
    )

    cob_test        = models.BooleanField(null=True, blank=True)  
    alcohol_test    = models.BooleanField(null=True, blank=True)
    ph_value        = models.FloatField(null=True, blank=True)
    mbtr_quick      = models.IntegerField(null=True, blank=True)  

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
            total_price=0.00
        )

    def __str__(self):
        return f"Composite Sample {self.id}"
    

