from django.urls import path
from .views import user_access, login
app_name = "accounts"

urlpatterns = [
    path('user-access/', user_access, name='user_access'),
    path('login/', login, name='login'),
]
