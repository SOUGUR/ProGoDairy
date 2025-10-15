from django.urls import path
from .views import accounting_base
app_name = "accounting"

urlpatterns = [
    path('accounting_base/', accounting_base, name='accounting_base'),
]
