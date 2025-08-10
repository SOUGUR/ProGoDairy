from django.db import models
from decimal import Decimal
from django.contrib.auth.models import User
from distribution.models import Route


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
        Route,
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
    tester = models.ForeignKey(
        "plants.Tester",
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

    # Pricing
    price_per_litre = models.DecimalField(
        max_digits=6, decimal_places=2, blank=True, null=True
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
    transfer = models.ForeignKey(
        "distribution.MilkTransfer",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="milk_lots",
    )

    bulk_cooler = models.ForeignKey(
        "collection_center.BulkCooler",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="milk_lots",
    )

    def __str__(self):
        return (
            f"{self.supplier.user.username} – {self.volume_l} L – {self.date_created}"
        )

    def evaluate_and_price(self):
        """
        Evaluate quality parameters and set price_per_litre and total_price
        """
        # Thresholds based on industry guidelines (simplified)
        THRESHOLDS = {
            "fat": 3.5,
            "snf": 8.5,
            "protein": 3.0,
            "urea_max": 70,  # mg/dL
            "bacteria_max": 50000,  # per mL
        }

        # Base price logic (per litre)
        base_price = Decimal("26.00")
        bonus = Decimal("0.00")

        # Quality Bonus system
        if self.fat_percent >= THRESHOLDS["fat"]:
            bonus += Decimal("1.50")
        if self.snf >= THRESHOLDS["snf"]:
            bonus += Decimal("1.00")
        if self.protein_percent >= THRESHOLDS["protein"]:
            bonus += Decimal("0.50")
        if self.urea_nitrogen <= THRESHOLDS["urea_max"]:
            bonus += Decimal("0.50")
        if self.bacterial_count <= THRESHOLDS["bacteria_max"]:
            bonus += Decimal("0.50")

        final_price_per_litre = base_price + bonus
        self.price_per_litre = final_price_per_litre
        self.total_price = round(Decimal(self.volume_l) * final_price_per_litre, 2)

        return self.total_price


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
