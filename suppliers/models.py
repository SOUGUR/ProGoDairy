from django.db import models
from decimal import Decimal, ROUND_HALF_UP
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.apps import apps


class Supplier(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.TextField()
    phone_number = models.CharField(
        max_length=15, help_text="Supplier's mobile number (10 digits)"
    )
    email = models.EmailField(blank=True, null=True)

    daily_capacity = models.FloatField(
        help_text="Litres the supplier commits to deliver every day"
    )
    total_dairy_cows = models.PositiveIntegerField()
    annual_output = models.FloatField(help_text="Total litres expected in a year")
    distance_from_plant = models.FloatField(
        help_text="Kilometres from supplier farm to the plant"
    )

    # Identity and Bank Details
    aadhar_number = models.CharField(
        max_length=12, help_text="Aadhar number of the supplier"
    )
    bank_account_number = models.CharField(max_length=30)
    bank_name = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=11)
    route = models.ForeignKey(
        "distribution.Route",
        related_name="suppliers",
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return f"{self.user.username} ({self.phone_number})"


class MilkLot(models.Model):
    """
    One 50 L (or other volume) can of milk supplied by a supplier.
    """

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    )

    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="lots"
    )
    employee = models.ForeignKey(
        "plants.Employee",
        on_delete=models.CASCADE,
        related_name="tested_lots",
        null=True,
        blank=True,
    )
    volume_l = models.FloatField(default=50.0)
    date_created = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    # Quality parameters
    fat_percent = models.FloatField()
    protein_percent = models.FloatField()
    lactose_percent = models.FloatField()
    total_solids = models.FloatField()
    snf = models.FloatField(verbose_name="Solids-Not-Fat")
    urea_nitrogen = models.FloatField(verbose_name="MUN (mg/dL)")
    bacterial_count = models.PositiveIntegerField()
    added_water_percent = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MaxValueValidator(100.0)],
        help_text="Percentage of water added (adulteration).",
    )

    # Pricing
    price_per_litre = models.DecimalField(
        max_digits=8, decimal_places=2, blank=True, null=True
    )
    total_price = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    bill = models.ForeignKey(
        "PaymentBill",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="milk_lots",
    )

    on_farm_tank = models.ForeignKey(
        "suppliers.OnFarmTank",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="milk_lots",
        help_text="The farm tank where this lot was stored before transport.",
    )

    bulk_cooler = models.ForeignKey(
        "collection_center.BulkCooler",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="milk_lots",
    )

    can_collection = models.ForeignKey(
        "suppliers.CanCollection",
        on_delete=models.CASCADE,
        related_name="milk_lots",
        null=True,
        blank=True,
    )

    def clean(self):
        storage_links = [self.bulk_cooler, self.can_collection, self.on_farm_tank]
        if sum(1 for link in storage_links if link is not None) > 1:
            raise ValidationError(
                "A milk lot can only be in one storage location at a time."
            )

    def save(self, *args, **kwargs):
        if not self.supplier_id:
            raise ValidationError("Supplier is required.")
        self.full_clean()
        super().save(*args, **kwargs)

    def evaluate_and_price(self):
        try:
            MilkPricingConfig = apps.get_model("milk", "MilkPricingConfig")
            config = MilkPricingConfig.objects.get(route=self.supplier.route)
        except MilkPricingConfig.DoesNotExist:
            raise ValidationError("No milk pricing configuration set. Please configure pricing first.")

        bonus = Decimal("0.00")

        if self.fat_percent >= config.fat_min:
            bonus += config.fat_bonus
        if self.snf >= config.snf_min:
            bonus += config.snf_bonus
        if self.protein_percent >= config.protein_min:
            bonus += config.protein_bonus
        if self.urea_nitrogen <= config.urea_max:
            bonus += config.urea_bonus
        if self.bacterial_count <= config.bacteria_max:
            bonus += config.bacteria_bonus

        if self.added_water_percent > config.added_water_max:
            self.status = "rejected"
            self.price_per_litre = Decimal("0.00")
            self.total_price = Decimal("0.00")
            return self.total_price
        elif self.added_water_percent > 0.0:
            bonus -= config.water_penalty_per_percent * Decimal(str(self.added_water_percent))

        final_price_per_litre = config.base_price + bonus
        if final_price_per_litre < Decimal("0.00"):
            final_price_per_litre = Decimal("0.00")

        self.price_per_litre = final_price_per_litre.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.total_price = (Decimal(self.volume_l) * self.price_per_litre).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        return self.total_price

    
    def __str__(self):
        return (
            f"{self.supplier.user.username} – {self.volume_l} L – {self.date_created}"
        )

class PaymentBill(models.Model):
    supplier = models.ForeignKey(
        Supplier, on_delete=models.CASCADE, related_name="bills"
    )
    date = models.DateField()
    total_volume_l = models.FloatField()
    total_value = models.DecimalField(max_digits=10, decimal_places=2)
    pdf_url = models.URLField(blank=True)

    is_paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)

    def calculate_totals(self):
        approved_lots = MilkLot.objects.filter(
            supplier=self.supplier, status="approved", date_created=self.date
        )
        self.total_volume_l = sum(lot.volume_l for lot in approved_lots)
        self.total_value = sum(
            lot.total_price for lot in approved_lots if lot.total_price
        )
        approved_lots.update(bill=self)
        self.save()

    def __str__(self):
        return f"Bill {self.id} – {self.supplier.user.username} – {self.date}"


class OnFarmTank(models.Model):
    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        help_text="Supplier who owns this farm tank.",
    )
    name = models.CharField(
        max_length=50,
        help_text="Tank name or code for easy identification (e.g., 'Tank-1').",
    )
    capacity_liters = models.PositiveIntegerField(
        validators=[MinValueValidator(2000), MaxValueValidator(15000)]
    )
    current_volume_liters = models.FloatField(
        default=0.0, help_text="Current amount of milk in the tank in liters."
    )
    temperature_celsius = models.FloatField(
        null=True, blank=True, help_text="Current milk temperature in Celsius."
    )

    is_stirred = models.BooleanField(default=False)

    filled_at = models.DateTimeField(null=True, blank=True)
    emptied_at = models.DateTimeField(null=True, blank=True)
    last_cleaned_at = models.DateTimeField(null=True, blank=True)
    last_sanitized_at = models.DateTimeField(null=True, blank=True)

    service_interval_days = models.PositiveSmallIntegerField(default=90)
    last_serviced_at = models.DateTimeField(null=True, blank=True)

    last_calibration_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="Date and time when the tank record was created."
    )

    def add_lots(self, *milk_lots):
        already_in_this_tank = [
            lot for lot in milk_lots if lot.on_farm_tank_id == self.id
        ]
        if already_in_this_tank:
            raise ValueError(
                f"Cannot add {len(already_in_this_tank)} milk lots: "
                "they are already assigned to this On-Farm Tank."
            )

        candidates = [
            lot
            for lot in milk_lots
            if lot.status == "pending" and lot.on_farm_tank_id is None
        ]

        proposed_volume = sum(lot.volume_l for lot in candidates)
        if self.current_volume_liters + proposed_volume > self.capacity_liters:
            raise ValueError(
                f"Cannot add {proposed_volume} liters. "
                f"Tank capacity {self.capacity_liters}L exceeded "
                f"(current volume: {self.current_volume_liters}L)."
            )

        for lot in candidates:
            lot.on_farm_tank = self
        MilkLot.objects.bulk_update(candidates, ["on_farm_tank"])

        self.current_volume_liters += proposed_volume
        self.save(update_fields=["current_volume_liters"])
        return len(candidates)

    def __str__(self):
        return f"{self.name} ({self.supplier.user.username})"


class CanCollection(models.Model):
    route = models.ForeignKey(
        "distribution.Route",
        on_delete=models.CASCADE,
        help_text="Distribution route along which cans are collected.",
    )
    name = models.CharField(
        max_length=50,
        help_text="Optional name or code for this can collection event (e.g., 'Morning Route A').",
    )
    total_volume_liters = models.FloatField(
        default=0.0, help_text="Total milk volume from all cans in this collection."
    )

    created_at = models.DateTimeField(
        auto_now_add=True, help_text="When this can collection record was created."
    )

    emptied_at = models.DateTimeField(null=True, blank=True)

    def add_lots(self, *milk_lots):
        already_in_this_collection = [
            lot for lot in milk_lots if lot.can_collection_id == self.id
        ]
        if already_in_this_collection:
            raise ValidationError(
                f"Cannot add {len(already_in_this_collection)} milk lots: "
                "they are already assigned to this can collection."
            )

        candidates = [
            lot
            for lot in milk_lots
            if lot.status == "pending" and lot.can_collection_id is None
        ]
        total_volume = 0
        for lot in candidates:
            total_volume += lot.volume_l
            lot.can_collection = self
        MilkLot.objects.bulk_update(candidates, ["can_collection"])

        self.total_volume_liters += total_volume
        self.save(update_fields=["total_volume_liters"])

        return len(candidates)

    def __str__(self):
        return f"Can Collection - {self.name} {self.created_at} ({self.route.name})"

