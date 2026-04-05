from django.urls import path

from .views import (list_composite_samples, manage_milk_route_pricings,
                    take_composite_sample, take_gate_sample)

app_name = "milk"

urlpatterns = [
    path('take-composite-sample/', take_composite_sample, name='take_composite_sample'),
    path('take-gate-sample/', take_gate_sample, name='take_gate_sample'),
    path('list-composite-samples/', list_composite_samples, name='list_composite_samples'),
    path('milk-route-pricings/', manage_milk_route_pricings, name='milk_route_pricings')
]