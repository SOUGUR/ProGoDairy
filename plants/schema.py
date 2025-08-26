import strawberry
import strawberry_django
from typing import List
from strawberry_django import field
from accounts.schema import UserType
from plants.models import Employee, Plant, Role
from typing import Optional

@strawberry_django.type(Role)
class RoleType:
    id: strawberry.auto
    name: strawberry.auto
    description: strawberry.auto

@strawberry_django.type(Employee)
class EmployeeType:
    id: strawberry.auto
    user: UserType
    employee_id: strawberry.auto
    phone_number: strawberry.auto
    address: strawberry.auto
    role: Optional[RoleType]
    routes: strawberry.auto 

@strawberry.type
class PlantType:
    id: strawberry.ID
    name: str

@strawberry.type
class Query:
    @field
    def testers(self) -> List[EmployeeType]:
        return Employee.objects.filter(role__name="tester")
    
    @field
    def employees(self) -> List[EmployeeType]:
        return Employee.objects.select_related("role", "user").all()

    @strawberry.field
    def plants(self) -> List[PlantType]:
        return Plant.objects.all()


schema = strawberry.Schema(query=Query)
