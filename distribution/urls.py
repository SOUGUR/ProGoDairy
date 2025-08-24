from django.urls import path
from .views import vehicle_list, create_milk_transfer, milk_transfer_list

app_name = "distribution"

urlpatterns = [
    path('vehicles/', vehicle_list, name='vehicle_list'),
    path('create_milk_transfer/', create_milk_transfer, name='create_milk_transfer'),
    path('milk_transfer_list/', milk_transfer_list, name='milk_transfer_list'),
]
