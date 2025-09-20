import strawberry
import strawberry_django
from typing import Optional, List
from decimal import Decimal
from datetime import date, datetime
from accounts.schema import RouteType
from strawberry_django import type as strawberry_django_type
from accounts.schema import UserType
from suppliers.models import Supplier, MilkLot, OnFarmTank
from distribution.models import Vehicle, Distributor
from plants.models import Employee, Role, Silo
from collection_center.models import BulkCooler

@strawberry.type
class RouteVolumeStats:
    route_name: str
    total_volume: Decimal
    
@strawberry.type
class MilkLotVolumeStatType:
    date: date
    status: str
    total_volume: float


@strawberry_django_type(Supplier)
class SupplierType:
    id: int
    user: "UserType"
    address: Optional[str]
    phone_number: Optional[str]
    email: Optional[str]
    daily_capacity: Optional[int]
    total_dairy_cows: Optional[int]
    annual_output: Optional[float]
    distance_from_plant: Optional[float]
    aadhar_number: Optional[str]
    bank_account_number: Optional[str]
    bank_name: Optional[str]
    ifsc_code: Optional[str]
    route: Optional[RouteType]

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
    @strawberry.field
    def is_occupied(self) -> bool:
        return self.is_available  

@strawberry.type
class PlantType:
    id: strawberry.ID
    name: str

@strawberry.input
class VehicleInput:
    distributor_id: int
    name: str
    vehicle_id: str
    capacity_liters: Optional[float] = None
    route_id: int

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
class CanCollectionType:
    id: int
    route: RouteType
    name: str
    total_volume_liters: float
    created_at: datetime

@strawberry.type
class AssignCanCollectionPayload:
    success: bool
    message: str

@strawberry.type
class PaymentBillType:
    id: int
    total_volume_l: float
    total_value: float
    is_paid: bool
    payment_date: Optional[date] = None

@strawberry.type
class OnFarmTankType:
    id: int
    supplier: SupplierType
    name: str
    capacity_liters: int
    current_volume_liters: float
    temperature_celsius: Optional[float]
    filled_at: Optional[datetime]
    emptied_at: Optional[datetime]
    last_cleaned_at: Optional[datetime]
    last_sanitized_at: Optional[datetime]
    service_interval_days: int
    last_serviced_at: Optional[datetime]
    last_calibration_date: Optional[datetime]
    created_at: datetime
    is_stirred: Optional[bool] = False
    @strawberry.field
    def milk_lots(self) -> List['MilkLotType']:
        return MilkLot.objects.filter(on_farm_tank_id=self.id)
    @strawberry.field
    def related_milk_transfers(self, info) -> List[MilkTransferType]:
        onFarm_Tanker = OnFarmTank.objects.get(id=self.id)
        return onFarm_Tanker.milk_transfers.all()
    @strawberry.field(name="sampleCount")
    def sample_count(self, info) -> int:
        onFarm_Tanker = OnFarmTank.objects.get(id=self.id)
        return onFarm_Tanker.samples.count()
    

@strawberry.type
class BulkCoolerType:
    id: int
    name: str
    capacity_liters: int
    current_volume_liters: float
    temperature_celsius: float
    route: RouteType  
    filled_at: Optional[datetime]
    emptied_at: Optional[datetime]
    last_cleaned_at: Optional[datetime]
    last_sanitized_at: Optional[datetime]
    service_interval_days: int
    last_serviced_at: Optional[datetime]
    last_calibration_date: Optional[datetime]
    created_at: datetime
    is_stirred: Optional[bool] = False
    @strawberry.field
    def milk_lots(self) -> List["MilkLotType"]:
        return MilkLot.objects.filter(bulk_cooler_id=self.id)
    @strawberry.field
    def related_milk_transfers(self, info) -> List[MilkTransferType]:
        cooler = BulkCooler.objects.get(id=self.id)
        return cooler.milk_transfers.all()
    @strawberry.field(name="sampleCount")
    def sample_count(self, info) -> int:
        cooler = BulkCooler.objects.get(id=self.id)
        return cooler.samples.count()

@strawberry.input
class UpdateTankerInput:
    id: int
    type: str  # "bulk_cooler" or "on_farm_tank"

    last_cleaned_at: Optional[datetime] = None
    last_sanitized_at: Optional[datetime] = None
    service_interval_days: Optional[int] = None
    last_serviced_at: Optional[datetime] = None
    last_calibration_date: Optional[datetime] = None

@strawberry.type
class UpdateTankerResponse:
    success: bool
    message: str

@strawberry.type
class MilkLotType:
    id: int
    supplier: SupplierType
    tester: Optional[EmployeeType] = strawberry_django.field(field_name="employee")
    volume_l: float
    fat_percent: float
    protein_percent: float
    lactose_percent: float
    total_solids: float
    snf: float
    urea_nitrogen: float
    bacterial_count: int
    added_water_percent: Optional[float]
    price_per_litre: Optional[Decimal]
    total_price: Optional[Decimal]
    status: str
    date_created: Optional[date]
    bill: Optional[PaymentBillType]
    bulk_cooler: Optional["BulkCoolerType"]
    on_farm_tank: Optional["OnFarmTankType"]
    can_collection: Optional["CanCollectionType"]



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
    @strawberry.field
    def completed_transfers(self) -> List["MilkTransferType"]:
        return self.incoming_transfers.filter(status="completed")