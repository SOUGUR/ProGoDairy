from django.contrib import admin
from .models import Supplier, MilkLot,PaymentBill
# Register your models here.
admin.site.register(Supplier)
admin.site.register(MilkLot)
admin.site.register(PaymentBill)
