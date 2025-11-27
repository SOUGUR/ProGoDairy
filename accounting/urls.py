from django.urls import path
from .views import accounting_dashboard, billing_and_payment
app_name = "accounting"

urlpatterns = [
    path('accounting_dashboard/', accounting_dashboard, name='accounting_dashboard'),
    path('billing_and_payment', billing_and_payment, name='billing_and_payment'),
]
