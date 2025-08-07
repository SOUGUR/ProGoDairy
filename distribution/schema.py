import strawberry
from typing import Optional, List
from strawberry_django import type as strawberry_django_type
from django.contrib.auth.models import User

from .models import Vehicle, Distributor, Route
from strawberry.types import Info
from django.core.exceptions import ObjectDoesNotExist


@strawberry_django_type(Route)
class RouteType:
    id: int
    name: str


@strawberry_django_type(User)
class UserType:
    id: int
    username: str
    email: str


@strawberry_django_type(Distributor)
class DistributorType:
    id: int
    address: str
    license_number: Optional[str]
    user: "UserType"


@strawberry_django_type(Vehicle)
class VehicleType:
    id: int
    name: str
    vehicle_id: str
    capacity_liters: Optional[float]
    distributor: Optional["DistributorType"] = None
    route: Optional["RouteType"] = None


@strawberry.input
class VehicleInput:
    distributor_id: int
    name: str
    vehicle_id: str
    capacity_liters: Optional[float] = None
    route_id: int


@strawberry.type
class Query:
    @strawberry.field
    def all_vehicles(self) -> List[VehicleType]:
        return Vehicle.objects.select_related('distributor', 'route').all()
    
    @strawberry.field
    def all_routes(self) -> List[RouteType]:
        return Route.objects.all()

    @strawberry.field
    def all_distributors(self) -> List[DistributorType]:
        return Distributor.objects.all()


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_vehicle(self, info: Info, input: VehicleInput) -> VehicleType:
        try:
            distributor = Distributor.objects.get(id=input.distributor_id)
        except ObjectDoesNotExist:
            raise Exception("Distributor not found")
        try:
            route = Route.objects.get(id=input.route_id)
        except ObjectDoesNotExist:
            raise Exception("Route not found")

        vehicle = Vehicle.objects.create(
            distributor=distributor,
            name=input.name,
            vehicle_id=input.vehicle_id,
            capacity_liters=input.capacity_liters,
            route=route,
        )
        return VehicleType(
            id=vehicle.id,
            name=vehicle.name,
            vehicle_id=vehicle.vehicle_id,
            capacity_liters=vehicle.capacity_liters,
        )


schema = strawberry.Schema(query=Query)
