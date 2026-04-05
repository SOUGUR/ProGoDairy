from django.contrib import admin

from .models import CanCollection, MilkLot, OnFarmTank, PaymentBill, Supplier

# Register your models here.
admin.site.register(Supplier)
admin.site.register(MilkLot)
admin.site.register(PaymentBill)
admin.site.register(OnFarmTank)
admin.site.register(CanCollection)
