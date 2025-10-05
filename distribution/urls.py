from django.urls import path
from .views import vehicle_list, create_milk_transfer, milk_transfer_list, add_get_vehicle_driver, vehicle_CIP_log

app_name = "distribution"

urlpatterns = [
    path('add_get_vehicle_driver/', add_get_vehicle_driver, name='add_get_vehicle_driver'),
     path('vehicle_CIP_log/', vehicle_CIP_log, name='vehicle_CIP_log'),
    path('vehicles/', vehicle_list, name='vehicle_list'),
    path('create_milk_transfer/', create_milk_transfer, name='create_milk_transfer'),
    path('milk_transfer_list/', milk_transfer_list, name='milk_transfer_list'),
]
