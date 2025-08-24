import strawberry
import strawberry_django
from typing import List
from strawberry_django import field
from accounts.schema import UserType
from plants.models import Employee, Plant

@strawberry_django.type(Employee)
class EmployeeType:
    id: strawberry.auto
    user: UserType
    employee_id: strawberry.auto
    phone_number: strawberry.auto
    address: strawberry.auto
    role: strawberry.auto   
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

    @strawberry.field
    def plants(self) -> List[PlantType]:
        return Plant.objects.all()


schema = strawberry.Schema(query=Query)
