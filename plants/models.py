from django.db import models
from suppliers.models import MilkLot
from distribution.models import Route
from django.contrib.auth.models import User

class Tester(models.Model):
    """
    Plant employee authorized to perform milk-quality tests.
    Includes extended tester-specific details.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    employee_id = models.CharField(max_length=20, unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    designation = models.CharField(max_length=100, default="Milk Quality Tester")
    routes = models.ManyToManyField(Route, related_name='testers', blank=True)

    def __str__(self):
        full_name = self.user.get_full_name()
        return f"Tester: {full_name or self.user.username} (ID: {self.employee_id})"



class Batch(models.Model):
    """
    Aggregated container of milk lots, after lab approval; stored in cold-room.
    """
    lots = models.ManyToManyField(MilkLot, through='BatchMembership')
    total_volume_l = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    use_by_date = models.DateField()

    def __str__(self):
        return f"Batch {self.id} – {self.total_volume_l} L"

    def calculate_total_volume(self):
        self.total_volume_l = sum([bm.volume_l for bm in self.batchmembership_set.all()])
        self.save()


class BatchMembership(models.Model):
    """
    Through table to record how much volume of each lot went into a batch.
    Useful when only part of a MilkLot is poured into a batch.
    """
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    milk_lot = models.ForeignKey(MilkLot, on_delete=models.CASCADE)
    volume_l = models.FloatField()

    class Meta:
        unique_together = ('batch', 'milk_lot')

    def __str__(self):
        return f"{self.volume_l} L from {self.milk_lot} in Batch {self.batch.id}"
