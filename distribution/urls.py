from django.urls import path
from .views import vehicle_list, create_milk_transfer

urlpatterns = [
    path('vehicles/', vehicle_list, name='vehicle_list'),
    path('milk-transfer/', create_milk_transfer, name='milk_transfer'),

]
