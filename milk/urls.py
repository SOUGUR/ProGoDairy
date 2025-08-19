from django.urls import path
from .views import take_composite_sample, list_composite_samples

app_name = "milk"

urlpatterns = [
    path('take-composite-sample/', take_composite_sample, name='take_composite_sample'),
    path('list-composite-samples/', list_composite_samples, name='list_composite_samples')
]