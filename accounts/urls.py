from django.urls import path

from .views import groq_chat_proxy, logout_view, user_access, user_flow

app_name = "accounts"

urlpatterns = [
    path('user-access/', user_access, name='user_access'),
    path('user-flow/', user_flow, name='user_flow'),
    path('logout/', logout_view, name='logout'),
    path('api/chat/', groq_chat_proxy, name='groq_chat_proxy'),
]
