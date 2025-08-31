import strawberry
import strawberry_django
from typing import List
from strawberry_django import field
from accounts.schema import UserType
from plants.models import Employee, Plant, Role, Silo
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

@strawberry_django.type(Silo)
class SiloType:
    id: strawberry.auto
    name: strawberry.auto
    code: strawberry.auto
    capacity_liters: strawberry.auto
    current_volume: strawberry.auto
    milk_type: strawberry.auto
    temperature: strawberry.auto
    status: strawberry.auto
    is_clean: strawberry.auto
    last_cleaned_at: strawberry.auto
    last_cleaned_by: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto
    @strawberry.field
    def plant_name(self) -> str:
        return self.plant.name

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
    
    @strawberry.field
    def silos_by_plant(self, info, plant_id: int) -> list[SiloType]:
        try:
            silos = Silo.objects.filter(plant_id=plant_id).select_related('last_cleaned_by', 'plant')
            return silos
        except Exception:
            return []
    


schema = strawberry.Schema(query=Query)
