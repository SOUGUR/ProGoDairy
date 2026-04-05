from typing import List

import strawberry
import strawberry_django
from django.contrib.auth.models import User
from strawberry_django import type as strawberry_django_type


@strawberry.type
class TokenResponse:
    access_token: str
    message: str

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
