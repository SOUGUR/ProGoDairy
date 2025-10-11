from django.urls import path
from .views import user_access, login, user_flow, logout_view
app_name = "accounts"

urlpatterns = [
    path('user-access/', user_access, name='user_access'),
    path('user-flow/', user_flow, name='user_flow'),
    path('login/', login, name='login'),
    path('logout/', logout_view, name='logout'),
]
