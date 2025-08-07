from django.contrib import admin
from .models import Route, Distributor, MilkTransfer, Vehicle

# Register your models here.
admin.site.register(Route)
admin.site.register(Distributor)
admin.site.register(MilkTransfer)
admin.site.register(Vehicle)