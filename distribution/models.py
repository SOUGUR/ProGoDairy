from django.db import models
from django.contrib.auth.models import User
from plants.models import Tester
from suppliers.models import Supplier

class Route(models.Model):
    """
    A named path that groups suppliers for daily pickup.
    A single route can be assigned to multiple distributors.
    """
    name = models.CharField(max_length=100, unique=True)
    tester = models.ForeignKey(
        Tester,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='routes'
    )
    suppliers = models.ManyToManyField(Supplier, related_name='routes')

    def __str__(self):
        return self.name


class Distributor(models.Model):
    """
    Entity that owns/operates trucks and is responsible for pickup via a specific route.
    Each distributor can be assigned to one route.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    address = models.TextField()
    license_number = models.CharField(max_length=100, null=True, blank=True)
    vehicle_name = models.CharField(max_length=100, null=True, blank=True)
    vehicle_id = models.CharField(max_length=50, null=True, blank=True)
    route = models.ForeignKey(
        Route,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='distributors'
    )

    def __str__(self):
        return f"{self.name} – {self.vehicle_name} ({self.vehicle_id})"
