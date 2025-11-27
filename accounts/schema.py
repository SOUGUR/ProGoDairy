from typing import List, Optional

import strawberry
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, User
from strawberry.types import Info

from dairy_project.graphql_types.auth import TokenResponse, UserType

from .utils import create_access_token, create_refresh_token, decode_token





@strawberry.input
class UserRightsInput:
    user_id: int
    is_active: bool
    is_staff: bool
    is_superuser: bool
    groups: List[str] 

@strawberry.type
class Query:
    @strawberry.field
    def get_user(self, info, id: int) ->  Optional[UserType]:
        try:
            return User.objects.get(pk=id)
        except User.DoesNotExist:
            return None

@strawberry.type
class Mutation:

    @strawberry.mutation
    def register(
        self,
        info: Info,
        username: str,
        password: str,
        first_name: str | None = None,
        last_name: str | None = None,
        email: str | None = None,
    ) -> str:
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name or "",
            last_name=last_name or "",
            email=email or "",
        )
        return f"User {user.username} registered successfully."

    @strawberry.mutation
    def login_user(self, info: Info, username: str, password: str) -> TokenResponse:
        request = info.context.request
        response = info.context.response

        user = authenticate(request, username=username, password=password)

        if not user:
            return TokenResponse(access_token="", message="Invalid credentials.")

        access = create_access_token(user)
        refresh = create_refresh_token(user)

        response.set_cookie(
            key="refresh_token",
            value=refresh,
            httponly=True,
            secure=True,
            samesite="Strict",
            max_age=60 * 60 * 24 * 30  
        )

        return TokenResponse(
            access_token=access,
            message=f"Welcome {user.username}! Redirecting..."
        )

    @strawberry.mutation
    def refresh_access(self, info: Info) -> TokenResponse:
        request = info.context.request
        refresh = request.COOKIES.get("refresh_token")

        if not refresh:
            return TokenResponse(access_token="", message="Refresh token missing.")

        try:
            payload = decode_token(refresh)

            if payload["type"] != "refresh":
                return TokenResponse(access_token="", message="Invalid refresh token type.")

            user = User.objects.get(id=payload["user_id"])
            new_access = create_access_token(user)

            return TokenResponse(access_token=new_access, message="Token refreshed.")

        except Exception:
            return TokenResponse(access_token="", message="Refresh token expired or invalid.")
    
    @strawberry.mutation
    def update_user_rights(self, info, input: UserRightsInput) -> UserType:
        try:
            user = User.objects.get(id=input.user_id)

            user.is_active = input.is_active
            user.is_staff = input.is_staff
            user.is_superuser = input.is_superuser
            user.save()

            user.groups.clear()
            for group_name in input.groups:
                group, _ = Group.objects.get_or_create(name=group_name)
                user.groups.add(group)

            user.save()

            return user

        except User.DoesNotExist:
            raise Exception(f"User with id={input.user_id} does not exist")
        except Exception as e:
            raise Exception(f"Failed to update user rights: {str(e)}")

schema = strawberry.Schema(query=Query, mutation=Mutation)

