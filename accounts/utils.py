import jwt
import arrow  
from django.conf import settings
from django.contrib.auth.models import User
from strawberry.types import Info
from django.shortcuts import redirect

ACCESS_EXPIRE_MIN = 10
REFRESH_EXPIRE_DAYS = 30

def create_access_token(user):
    payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": arrow.utcnow().shift(minutes=+ACCESS_EXPIRE_MIN).int_timestamp,
        "type": "access"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def create_refresh_token(user):
    payload = {
        "user_id": user.id,
        "username": user.username,
        "exp": arrow.utcnow().shift(days=+REFRESH_EXPIRE_DAYS).int_timestamp,
        "type": "refresh"
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

def decode_token(token):
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])


def jwt_login_required(view_func):
    def wrapper(request, *args, **kwargs):
        refresh = request.COOKIES.get("refresh_token")

        if not refresh:
            return redirect("home")

        try:
            payload = decode_token(refresh)

            if payload["type"] != "refresh":
                return redirect("home")

            request.user = User.objects.get(id=payload["user_id"])

        except Exception:
            return redirect("home")

        return view_func(request, *args, **kwargs)

    return wrapper

def get_authenticated_user(info: Info):
    auth_header = info.context.request.headers.get("Authorization")

    if not auth_header:
        raise Exception("Authorization header missing")

    token = auth_header.replace("Bearer ", "")

    payload = decode_token(token)

    if payload["type"] != "access":
        raise Exception("Invalid token type")

    return User.objects.get(id=payload["user_id"])
