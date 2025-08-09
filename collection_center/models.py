
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from suppliers.models import MilkLot


class BulkCooler(models.Model):
    route = models.ForeignKey(
        "distribution.Route",
        on_delete=models.CASCADE,
        related_name="bulk_coolers",
        help_text="Collection centre / BMCU where this cooler is installed.",
    )
    name = models.CharField(max_length=50, help_text="Cooler-1, Cooler-2 …")
    capacity_liters = models.PositiveIntegerField(
        validators=[MinValueValidator(300), MaxValueValidator(5000)]
    )
    current_volume_liters = models.FloatField(default=0.0)
    temperature_celsius = models.FloatField(
        default=4.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(8.0)],
        help_text="Current temperature in °C",
    )
    last_stirred_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.route.name} – {self.name} ({self.capacity_liters} L)"

    def add_lots(self, *milk_lots):
        candidates = [
            lot for lot in milk_lots
            if lot.status == 'approved' and lot.bulk_cooler_id is None
        ]

        proposed_volume = sum(lot.volume_l for lot in candidates)
        if self.current_volume_liters + proposed_volume > self.capacity_liters:
            return 0

        for lot in candidates:
            lot.bulk_cooler = self
        MilkLot.objects.bulk_update(candidates, ['bulk_cooler'])

        self.current_volume_liters += proposed_volume
        self.save(update_fields=['current_volume_liters'])
        return len(candidates) 


class CompositeSample(models.Model):
    
    bulk_cooler = models.ForeignKey(
        BulkCooler,
        on_delete=models.CASCADE,
        related_name="composite_samples",
    )
    transfer = models.OneToOneField(
        "distribution.MilkTransfer",
        on_delete=models.CASCADE,
        related_name="composite_sample",
        null=True,
        blank=True,
        help_text="Linked once the tanker is actually loaded.",
    )
    sampled_at = models.DateTimeField(auto_now_add=True)

    # LAB RESULTS (plant gate)
    fat_percent = models.FloatField(null=True, blank=True)
    snf_percent = models.FloatField(null=True, blank=True)
    protein_percent = models.FloatField(null=True, blank=True)
    bacterial_count = models.PositiveIntegerField(null=True, blank=True)
    antibiotic_residue = models.BooleanField(
        default=False,
        help_text="True if β-lactams or other residues detected.",
    )
    added_water = models.BooleanField(default=False)
    passed = models.BooleanField(null=True)

    def __str__(self):
        return f"Composite {self.id} – {self.bulk_cooler} – {self.sampled_at:%d-%b %H:%M}"