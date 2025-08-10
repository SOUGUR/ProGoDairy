from django.urls import path
from .views import user_access
app_name = "accounts"

urlpatterns = [
    path('user-access/', user_access, name='user_access'),
]
