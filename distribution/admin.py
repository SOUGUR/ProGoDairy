from django.contrib import admin

from .models import (Distributor, GatePass, GatePassQC, MilkTransfer, Route,
                     Seal, Vehicle)

# Register your models here.
admin.site.register(Route)
admin.site.register(Distributor)
admin.site.register(MilkTransfer)
admin.site.register(Vehicle)
admin.site.register(GatePass)
admin.site.register(GatePassQC)
admin.site.register(Seal)