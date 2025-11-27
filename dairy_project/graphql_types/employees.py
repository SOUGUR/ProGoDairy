from typing import Optional

import strawberry
from strawberry_django import type as strawberry_django_type

from plants.models import Employee, Role

from .auth import UserType

@strawberry_django_type(Role)
class RoleType:
    id: strawberry.auto
    name: strawberry.auto
    description: strawberry.auto

@strawberry_django_type(Employee)
class EmployeeType:
    id: strawberry.auto
    user: UserType
    employee_id: strawberry.auto
    phone_number: strawberry.auto
    address: strawberry.auto
    role: Optional[RoleType]
    routes: strawberry.auto
