from django.urls import path
from .views import pump_into_silos

app_name = "plants"

urlpatterns = [
    path('pump_into_silos/', pump_into_silos, name='pump_into_silos'),
]