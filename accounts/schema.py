import strawberry
from strawberry.types import Info
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login

@strawberry.type
class Query:
    hello: str = "Hello, GraphQL!"  

@strawberry.type
class Mutation:

    @strawberry.mutation
    def register(self, info: Info, username: str, email: str, password: str) -> str:
        user = User.objects.create_user(username=username, email=email, password=password)
        return f"User {user.username} registered successfully."

    @strawberry.mutation
    def login_user(self, info: Info, username: str, password: str) -> str:
        request = info.context.request
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return f"Welcome, {user.username}!"
        return "Invalid credentials."

schema = strawberry.Schema(query=Query, mutation=Mutation)

