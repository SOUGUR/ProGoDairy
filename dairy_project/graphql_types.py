import strawberry
import strawberry_django
from typing import Optional, List
from decimal import Decimal
from datetime import date, datetime
from accounts.schema import RouteType
from strawberry_django import type as strawberry_django_type
from accounts.schema import UserType
from suppliers.models import Supplier, MilkLot, OnFarmTank
from distribution.models import Vehicle, Distributor, CIPRecord
from plants.models import Employee, Role, Silo
from collection_center.models import BulkCooler
from milk.models import CompositeSample
from strawberry import auto
from enum import Enum

@strawberry.type
class RouteVolumeStats:
    route_name: str
    total_volume: Decimal
    
@strawberry.type
class MilkLotVolumeStatType:
    date: date
    status: str
    total_volume: float

@strawberry.type
class SupplierVolumeStatType:
    supplier_id: int
    supplier_name: str
    status: str
    total_volume: float

@strawberry.type
class BillSummaryType:
    is_paid: bool
    total_value: float
    total_volume_l: float


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


@strawberry.type
class VehicleDriverType:
    id: int
    name: str
    mobile: str
    licence_no: str
    licence_expiry: date
    route: RouteType | None
    is_active: bool


@strawberry.input
class VehicleDriverInput:
    name: str
    mobile: str
    licence_no: str
    licence_expiry: date
    route_id: int | None = None
    is_active: bool = True  

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
    

@strawberry_django.type(CIPRecord)
class CIPRecordType:
    id: auto
    certificate_no: auto
    wash_type: auto
    started_at: auto
    finished_at: auto
    expiry_at: auto
    caustic_temp_c: auto
    acid_temp_c: auto
    caustic_conc_pct: auto
    acid_conc_pct: auto
    final_rinse_cond_ms: auto
    operator_code: auto
    passed: auto
    vehicle: "VehicleType" 


@strawberry.input
class CIPRecordInput:
    vehicle_id: int
    certificate_no: str
    wash_type: str
    started_at: datetime
    finished_at: datetime
    expiry_at: datetime
    caustic_temp_c: Optional[float] = None
    acid_temp_c: Optional[float] = None
    caustic_conc_pct: Optional[float] = None
    acid_conc_pct: Optional[float] = None
    final_rinse_cond_ms: Optional[float] = None
    operator_code: str
    passed: bool = True


@strawberry.input
class CIPRecordUpdateInput:
    id: int
    certificate_no: Optional[str] = None
    wash_type: Optional[str] = None
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    expiry_at: Optional[datetime] = None
    caustic_temp_c: Optional[float] = None
    acid_temp_c: Optional[float] = None
    caustic_conc_pct: Optional[float] = None
    acid_conc_pct: Optional[float] = None
    final_rinse_cond_ms: Optional[float] = None
    operator_code: Optional[str] = None
    passed: Optional[bool] = None

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

    vehicle: Optional["VehicleType"]
    destination: Optional["PlantType"]

    departure_weight_kg: Optional[float]
    arrival_weight_kg: Optional[float]

    bulk_cooler: Optional["BulkCoolerType"]
    on_farm_tank: Optional["OnFarmTankType"]
    can_collection: Optional["CanCollectionType"]

    @strawberry.field(name="gateSamplesCount")
    def gate_sample_count(self, info) -> int:
        if not self.vehicle:
            return 0

        samples_qs = CompositeSample.objects.filter(
            vehicle__transfers__id=self.id
        )
        return samples_qs.count()
    
    @strawberry.field
    def related_composite_samples(self, info) -> List["CompositeSampleType"]:
        filters = {}

      
        if self.vehicle:
            filters["vehicle"] = self.vehicle

        if self.bulk_cooler:
            filters["bulk_cooler"] = self.bulk_cooler
        elif self.on_farm_tank:
            filters["on_farm_tank"] = self.on_farm_tank
        elif self.can_collection:
            filters["bulk_cooler__isnull"] = True
            filters["on_farm_tank__isnull"] = True

        return CompositeSample.objects.filter(**filters)

@strawberry.enum
class SampleTypeEnum(Enum):
    INSTANT_GATE_TESTS = "instant-gate tests"
    SOCIETY_TEST = "society test"

@strawberry.input
class CompositeSampleInput:
    bulk_cooler_id: Optional[int] = None
    on_farm_tank_id: Optional[int] = None
    vehicle_id: Optional[str] = None
    remark: Optional[str] = None
    sample_volume_ml: Optional[int] = 50
    temperature_c: Optional[float] = 4.0
    is_stirred:Optional[bool] = False
    
    

@strawberry.input
class UpdateCompositeSampleInput:
    id: int
    received_at_lab: Optional[datetime] = None
    remark: str | None = None
    fat_percent: float | None = None
    snf_percent: float | None = None
    protein_percent: float | None = None
    bacterial_count: int | None = None
    antibiotic_residue: bool | None = None
    added_water_percent: float | None = None
    passed: str | None = None   

    sample_type: Optional[str] = None 
    cob_test: Optional[bool] = None
    alcohol_test: Optional[bool] = None
    ph_value: Optional[float] = None
    mbtr_quick: Optional[int] = None


@strawberry.type
class CompositeSampleType:
    id: int
    sample_volume_ml: int
    collected_at: datetime
    temperature_c: float
    received_at_lab: Optional[datetime]
    remark: Optional[str]

    fat_percent: Optional[float]
    snf_percent: Optional[float]
    protein_percent: Optional[float]
    bacterial_count: Optional[int]
    antibiotic_residue: bool
    added_water_percent: float
    passed: Optional[str]

    cob_test: Optional[bool] = None
    alcohol_test: Optional[bool] = None
    ph_value: Optional[float] = None
    mbtr_quick: Optional[int] = None

    bulk_cooler: Optional["BulkCoolerType"]
    on_farm_tank: Optional["OnFarmTankType"]
    vehicle: Optional["VehicleType"]
    sample_type: SampleTypeEnum


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

@strawberry.input
class MilkPricingConfigInput:
    routeId: int
    base_price: Optional[Decimal] = None
    added_water_max: Optional[float] = None

    fat_min: Optional[float] = None
    fat_bonus: Optional[Decimal] = None

    snf_min: Optional[float] = None
    snf_bonus: Optional[Decimal] = None

    protein_min: Optional[float] = None
    protein_bonus: Optional[Decimal] = None

    urea_max:Optional[float] = None
    urea_bonus: Optional[Decimal] = None

    bacteria_max: Optional[int] = None
    bacteria_bonus: Optional[Decimal] = None

    water_penalty_per_percent: Optional[Decimal] = None

@strawberry.type
class MilkPricingConfigType:
    id: int
    base_price: Decimal
    added_water_max: float

    fat_min: float
    fat_bonus: Decimal

    snf_min: float
    snf_bonus: Decimal

    protein_min: float
    protein_bonus: Decimal

    urea_max: float
    urea_bonus: Decimal

    bacteria_max: int
    bacteria_bonus: Decimal

    water_penalty_per_percent: Decimal

    updated_at: datetime
    route: RouteType 

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
    

@strawberry.type
class InvoiceType:
    supplier_name: str
    route_name: Optional[str]
    last_supply_date: date
    total_due: float
    amount_paid: float
    status: str