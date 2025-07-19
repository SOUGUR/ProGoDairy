from django import forms
from .models import Supplier

class SupplierProfileForm(forms.ModelForm):
    class Meta:
        model = Supplier
        fields = ['name', 'contact_email', 'contact_phone', 'address', 'supply_capacity']
