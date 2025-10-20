
from django.db import models
from django.utils import timezone
from decimal import Decimal


class MilkPaymentInvoice(models.Model):
    id = models.BigAutoField(primary_key=True)
    invoice_date = models.DateField(db_index=True)
    invoice_prefix = models.CharField(max_length=50, default="MLK/")
    invoice_num = models.CharField(max_length=50, unique=True, db_index=True)

    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.CASCADE,
        related_name="milk_payment_invoices",
    )

    is_cancelled = models.BooleanField(default=False, db_index=True)
    cancel_reason = models.CharField(max_length=50, blank=True, null=True)
    cancel_date = models.DateTimeField(blank=True, null=True)

    total_amount_paid = models.DecimalField(max_digits=12, decimal_places=3, default=0.000)
    total_value = models.DecimalField(max_digits=12, decimal_places=3, default=0.000)

    STATUS_PENDING = "pending"
    STATUS_PART = "partial"
    STATUS_PAID = "paid"
    PAYMENT_STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_PART, "Partial"),
        (STATUS_PAID, "Paid"),
    ]
    payment_status = models.CharField(
        max_length=15,
        choices=PAYMENT_STATUS_CHOICES,
        default=STATUS_PENDING,
        db_index=True,
    )
    invoice_paid_date = models.DateTimeField(blank=True, null=True, db_index=True)
    updated_date = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "milk_payment_invoice"
        unique_together = [("supplier", "invoice_date")]
        ordering = ["-invoice_date", "-id"]
        indexes = [
            models.Index(fields=["supplier", "-invoice_date"]),
            models.Index(fields=["payment_status", "-invoice_date"]),
        ]

    def __str__(self):
        return f"{self.invoice_prefix}{self.invoice_num} – {self.supplier} – {self.invoice_date}"

    def add_payment(self, amount):
        amount = Decimal(str(amount))
        if amount <= 0:
            raise ValueError("Payment amount must be positive.")
        self.total_amount_paid += amount
        self._update_payment_status()
        self.save(update_fields=["total_amount_paid", "payment_status", "invoice_paid_date"])

    def _update_payment_status(self):
        """Sync payment status and invoice_paid_date"""
        if self.total_amount_paid >= self.total_value:
            self.payment_status = self.STATUS_PAID
            self.invoice_paid_date = timezone.now()
        elif self.total_amount_paid > 0:
            self.payment_status = self.STATUS_PART
            self.invoice_paid_date = None
        else:
            self.payment_status = self.STATUS_PENDING
            self.invoice_paid_date = None

    def recalculate_totals(self):
        """Recalculate totals based on related invoice items"""
        totals = self.items.aggregate(
            total=models.Sum("total_price"),
        )
        self.total_value = totals["total"] or Decimal("0.000")
        self.save(update_fields=["total_value"])



class MilkPaymentInvoiceItem(models.Model):
    id = models.BigAutoField(primary_key=True)
    invoice = models.ForeignKey(
        "MilkPaymentInvoice",
        on_delete=models.CASCADE,
        related_name="items",
    )
    milk_lot = models.OneToOneField(
        "suppliers.MilkLot",
        on_delete=models.CASCADE,
        related_name="payment_item",
        limit_choices_to={"status": "approved"},
    )
    qty_l = models.DecimalField(max_digits=12, decimal_places=2)
    price_per_litre = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "milk_payment_invoice_item"
        ordering = ["invoice", "id"]

    def __str__(self):
        return f"{self.invoice} – {self.milk_lot}"
