
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from suppliers.models import MilkLot

class BulkCoolerLog(models.Model):
    bulk_cooler = models.ForeignKey(
        'collection_center.BulkCooler',
        on_delete=models.CASCADE,
        related_name="logs"
    )
    log_date = models.DateTimeField()
    
    volume_liters = models.FloatField()
    temperature_celsius = models.FloatField()
    
    filled_at = models.DateTimeField(null=True, blank=True)
    emptied_at = models.DateTimeField(null=True, blank=True)
    last_cleaned_at = models.DateTimeField(null=True, blank=True)
    last_sanitized_at = models.DateTimeField(null=True, blank=True)
    last_calibration_date = models.DateTimeField(null=True, blank=True)
    last_serviced_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('bulk_cooler', 'log_date')

    def __str__(self):
        return f"{self.bulk_cooler.name} log – {self.log_date}"


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

    filled_at = models.DateTimeField(null=True, blank=True)
    emptied_at = models.DateTimeField(null=True, blank=True)
    last_cleaned_at = models.DateTimeField(null=True, blank=True)
    last_sanitized_at = models.DateTimeField(null=True, blank=True)
    is_stirred = models.BooleanField(default=False)

    service_interval_days = models.PositiveSmallIntegerField(default=90) 
    last_serviced_at = models.DateTimeField(null=True, blank=True)

    last_calibration_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def add_lots(self, *milk_lots):
        already_in_this_cooler = [lot for lot in milk_lots\
                                if lot.bulk_cooler_id == self.id]
        if already_in_this_cooler:
            raise ValueError(
                f"Cannot add {len(already_in_this_cooler)} milk lots: "
                "they are already assigned to this bulk cooler."
            )

        candidates = [
            lot for lot in milk_lots
            if lot.status == 'pending'
            and lot.bulk_cooler_id is None  
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
    
    
    def is_in_use(self):
        return self.bulkcooler_set.exists()

    def __str__(self):
        return f"{self.route.name} – {self.name} - {self.created_at} ({self.capacity_liters} L)"


