from django.urls import path
from .views import assign_cooler_tank

urlpatterns = [
    path('assign-cooler-tank/', assign_cooler_tank, name='cooler_tank'),

]