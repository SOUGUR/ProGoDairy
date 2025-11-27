from django.urls import path
from .views import pump_into_silos, tanker_logs, calibration_sanitation_records, dashboard

app_name = "plants"

urlpatterns = [
    path('pump_into_silos/', pump_into_silos, name='pump_into_silos'),
    path('tanker_logs/', tanker_logs, name='tanker_logs'),
    path('sanitation_records/', calibration_sanitation_records, name='sanitation_records'),
    path('dashboard/', dashboard, name='dashboard'),
]