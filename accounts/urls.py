from django.urls import path
from .views import user_access, login, user_flow, logout_view, groq_chat_proxy
app_name = "accounts"

urlpatterns = [
    path('user-access/', user_access, name='user_access'),
    path('user-flow/', user_flow, name='user_flow'),
    path('login/', login, name='login'),
    path('logout/', logout_view, name='logout'),
    path('api/chat/', groq_chat_proxy, name='groq_chat_proxy'),
]
