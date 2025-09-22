import strawberry
from strawberry.types import Info
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate, login
from strawberry_django import type as strawberry_django_type
from distribution.models import Route
from typing import List, Optional

@strawberry_django_type(User)
class UserType:
    id: int
    username: str
    email: str
    is_active: bool
    is_staff: bool
    is_superuser: bool

    @strawberry.field
    def groups(self, info) -> List[str]:
        return [group.name for group in self.groups.all()]


@strawberry_django_type(Route)
class RouteType:
    id: int
    name: str

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
    def login_user(self, info: Info, username: str, password: str) -> str:
        request = info.context.request
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return f"Welcome, {user.username}!"
        return "Invalid credentials."
    
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

