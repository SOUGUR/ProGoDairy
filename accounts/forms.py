from django import forms
from django.contrib.auth.models import User

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    ROLE_CHOICES = [
        ('SUPPLIER', 'Supplier'),
        ('EMPLOYEE', 'Plant Employee'),
        ('DISTRIBUTOR', 'Distributor'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get("password")
        cpwd = cleaned_data.get("confirm_password")
        if pwd and cpwd and pwd != cpwd:
            self.add_error('confirm_password', "Passwords do not match")
        return cleaned_data
