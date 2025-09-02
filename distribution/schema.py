import strawberry
from typing import Optional, List
from strawberry_django import type as strawberry_django_type
from datetime import datetime
from plants.schema import PlantType
from .models import Vehicle, Distributor, Route, MilkTransfer
from collection_center.schema import BulkCoolerType
from suppliers.schema import OnFarmTankType, CanCollectionType
from suppliers.models import OnFarmTank, CanCollection
from collection_center.models import BulkCooler
from django.core.exceptions import ValidationError 
from plants.models import Plant
from strawberry.types import Info
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Exists, OuterRef
from accounts.schema import UserType, RouteType
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone



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

@strawberry.input
class MilkTransferInput:
    source_type: str
    source_id: int
    vehicle_id: Optional[int] = None
    destination_id: Optional[int] = None
    status: Optional[str] = "scheduled"
    transfer_date: Optional[datetime] = None
    arrival_datetime :Optional[datetime] = None
    remarks : Optional[str] = None

@strawberry.input
class MilkTransferUpdateInput:
    id: int
    arrival_datetime: datetime
    remarks: Optional[str] = None

@strawberry.type
class MilkTransferType:
    id: int
    source_type: Optional[str]           
    transfer_date: datetime             
    arrival_datetime: Optional[datetime] 
    status: str                          
    total_volume: Optional[float]      
    remarks: Optional[str]             

    # ForeignKey relationships
    vehicle: Optional["VehicleType"]
    destination: Optional["PlantType"]

    # Sources (since model allows multiple)
    bulk_cooler: Optional["BulkCoolerType"]
    on_farm_tank: Optional["OnFarmTankType"]
    can_collection: Optional["CanCollectionType"]



@strawberry.type
class Query:
    @strawberry.field
    def all_vehicles(self) -> List[VehicleType]:
        return Vehicle.objects.select_related('distributor', 'route').all()
    
    @strawberry.field
    def all_routes(self) -> List[RouteType]:
        return Route.objects.all()
    
    @strawberry.field
    def vehicles_by_route(self, route_id: int) -> List[VehicleType]:
        return Vehicle.objects.filter(route_id=route_id)
    
    @strawberry.field
    def available_vehicles_by_route(self, route_id: int) -> List[VehicleType]:
        has_active_transfer = MilkTransfer.objects.filter(
            vehicle=OuterRef('pk'),  
            status__in=['scheduled', 'in_transit']
        )

        return Vehicle.objects.filter(
            route_id=route_id
        ).annotate(
            is_active_transfer=Exists(has_active_transfer)
        ).filter(
            is_active_transfer=False  
        )

    @strawberry.field
    def all_distributors(self) -> List[DistributorType]:
        return Distributor.objects.all()
    
    @strawberry.field
    def milk_transfers(
        self, info: Info, status: Optional[str] = None
    ) -> List[MilkTransferType]:
        milk_transfers = MilkTransfer.objects.all().order_by('-transfer_date')

        if status:
            milk_transfers = milk_transfers.filter(status=status)

        return milk_transfers
        
    @strawberry.field
    def get_completed_milk_transfers_by_plant(
        self, 
        info: Info, 
        plant_id: int, 
    ) -> List[MilkTransferType]:
        milk_transfers = MilkTransfer.objects.filter(status="completed", destination_id=plant_id)
        return milk_transfers


    @strawberry.field
    def milk_transfer_by_id(
        self, info: Info,
        id: int
    ) -> Optional[MilkTransferType]:
        try:
            return MilkTransfer.objects.get(id=id)
        except MilkTransfer.DoesNotExist:
            return None



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
    
    @strawberry.mutation
    def create_milk_transfer(self, info: Info, input: MilkTransferInput) -> MilkTransferType:
        try:
            vehicle = None
            if input.vehicle_id:
                vehicle = Vehicle.objects.get(id=input.vehicle_id)

            destination = None
            if input.destination_id:
                destination = Plant.objects.get(id=input.destination_id)

            transfer = MilkTransfer(
                source_type=input.source_type,
                vehicle=vehicle,
                destination=destination,
                status=input.status or 'scheduled',
            )

            now = timezone.now()
            if input.source_type == "bulk_cooler":
                source = BulkCooler.objects.get(id=input.source_id)
                transfer.bulk_cooler = source
                source.emptied_at = now
                source.save(update_fields=["emptied_at"])
            elif input.source_type == "on_farm_tank":
                source = OnFarmTank.objects.get(id=input.source_id)
                transfer.on_farm_tank = source
                source.emptied_at = now
                source.save(update_fields=["emptied_at"])
            elif input.source_type == "can_collection":
                source = CanCollection.objects.get(id=input.source_id)
                transfer.can_collection = source
                source.emptied_at = now
                source.save(update_fields=["emptied_at"])
            else:
                raise ValidationError("Invalid source_type provided. Must be one of: bulk_cooler, on_farm_tank, can_collection.")

            transfer.full_clean()
            transfer.save()
            transfer.calculate_total_volume()
        except DjangoValidationError:
            return ValidationError(
                "Milk Transfer for the selected tanker already created"
            )
    
        except Exception:
            return DjangoValidationError(
                "Error in creating the Milk Transfer, check the inputs again"
            )

    
    @strawberry.mutation
    def update_milktransfer(
        self, info, input: MilkTransferUpdateInput
    ) -> Optional["MilkTransferType"]:
        try:
            transfer = MilkTransfer.objects.get(id=input.id)
            transfer.arrival_datetime = input.arrival_datetime
            transfer.remarks = input.remarks
            transfer.status = "completed"
            transfer.save(update_fields=["arrival_datetime", "remarks", "status"])
            return transfer
        except MilkTransfer.DoesNotExist:
            return None


schema = strawberry.Schema(query=Query, mutation= Mutation)
