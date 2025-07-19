from django.urls import path
from .views import custom_login_view, register

urlpatterns = [
    path('login/', custom_login_view, name='custom_login'),
    path('register/', register, name='register'),
]
