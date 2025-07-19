from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid
from suppliers.models import Supplier
from plants.models import DairyPlant, PlantEmployee

# milk lot represents milk collected in one container
class MilkLot(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='milk_lots')
    plant = models.ForeignKey(DairyPlant, on_delete=models.CASCADE, related_name='milk_lots')
    lot_number = models.CharField(max_length=50, unique=True)
    volume = models.FloatField()
    storage_date = models.DateTimeField()
    expiry_date = models.DateTimeField()
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['storage_date']

    def __str__(self):
        return f"Lot {self.lot_number} from {self.supplier.name}"

    def set_expiry_date(self, days=7):
        self.expiry_date = self.storage_date + timedelta(days=days)
        self.save()

    @classmethod
    def get_next_to_expire(cls, plant):
        return cls.objects.filter(plant=plant, is_accepted=True, expiry_date__gte=timezone.now()).order_by('expiry_date')

class MilkTest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    milk_lot = models.ForeignKey(MilkLot, on_delete=models.CASCADE, related_name='tests')
    tester = models.ForeignKey(PlantEmployee, on_delete=models.SET_NULL, null=True, related_name='tests_conducted')
    fat_content = models.FloatField()
    ph_level = models.FloatField()
    bacterial_count = models.IntegerField()
    water_content = models.FloatField()
    passed = models.BooleanField(default=False)
    comments = models.TextField(blank=True)
    test_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['test_date']

    def __str__(self):
        return f"Test for Lot {self.milk_lot.lot_number} ({'Passed' if self.passed else 'Failed'})"

    def evaluate_test(self):
        thresholds = {
            'fat_content': 3.5,
            'ph_level_min': 6.5,
            'ph_level_max': 6.8,
            'bacterial_count': 100000,
            'water_content': 10.0,
        }
        self.passed = (
            self.fat_content >= thresholds['fat_content'] and
            thresholds['ph_level_min'] <= self.ph_level <= thresholds['ph_level_max'] and
            self.bacterial_count <= thresholds['bacterial_count'] and
            self.water_content <= thresholds['water_content']
        )
        if self.passed:
            self.milk_lot.is_accepted = True
            self.milk_lot.set_expiry_date()
            Payment.objects.create(
                milk_lot=self.milk_lot,
                supplier=self.milk_lot.supplier,
                plant=self.milk_lot.plant,
                volume=self.milk_lot.volume,
                rate_per_liter=self.milk_lot.plant.milk_rate,
                total_amount=self.milk_lot.volume * self.milk_lot.plant.milk_rate,
                status='PENDING'
            )
        self.milk_lot.save()
        self.save()

class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    milk_lot = models.ForeignKey(MilkLot, on_delete=models.CASCADE, related_name='payments')
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, related_name='payments')
    plant = models.ForeignKey(DairyPlant, on_delete=models.CASCADE, related_name='payments')
    volume = models.FloatField()
    rate_per_liter = models.FloatField()
    total_amount = models.FloatField()
    status = models.CharField(max_length=20, choices=[
        ('PENDING', 'Pending'),
        ('PAID', 'Paid'),
        ('CANCELLED', 'Cancelled'),
    ], default='PENDING')
    payment_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Payment of ${self.total_amount} for Lot {self.milk_lot.lot_number} to {self.supplier.name}"

    def mark_as_paid(self):
        self.status = 'PAID'
        self.payment_date = timezone.now()
        self.save()

    @classmethod
    def generate_payment_report(cls, supplier, start_date=None, end_date=None):
        queryset = cls.objects.filter(supplier=supplier)
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)
        report = []
        for payment in queryset:
            test = payment.milk_lot.tests.first()
            report.append({
                'lot_number': payment.milk_lot.lot_number,
                'volume': payment.volume,
                'rate_per_liter': payment.rate_per_liter,
                'total_amount': payment.total_amount,
                'status': payment.status,
                'payment_date': payment.payment_date,
                'test_result': 'Passed' if test and test.passed else 'Failed',
                'test_comments': test.comments if test else 'No test conducted',
            })
        rejected_lots = MilkLot.objects.filter(supplier=supplier, is_accepted=False)
        if start_date:
            rejected_lots = rejected_lots.filter(created_at__gte=start_date)
        if end_date:
            rejected_lots = rejected_lots.filter(created_at__lte=end_date)
        for lot in rejected_lots:
            test = lot.tests.first()
            report.append({
                'lot_number': lot.lot_number,
                'volume': lot.volume,
                'rate_per_liter': 0.0,
                'total_amount': 0.0,
                'status': 'REJECTED',
                'payment_date': None,
                'test_result': 'Failed',
                'test_comments': test.comments if test else 'No test conducted',
            })
        return report
