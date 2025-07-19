from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_supplier_profile, name='create_supplier_profile'),
    path('dashboard/', views.supplier_dashboard, name='supplier_dashboard'),
]
