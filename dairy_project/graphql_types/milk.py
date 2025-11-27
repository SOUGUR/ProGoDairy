from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Annotated, List, Optional

import strawberry
import strawberry_django
from strawberry_django import type as strawberry_django_type

from milk.models import CompositeSample
from suppliers.models import MilkLot

from .billing import PaymentBillType
from .employees import EmployeeType
from .routes import RouteType
from .suppliers import SupplierType

if TYPE_CHECKING:
    from .distribution import VehicleType
    from .plants import PlantType
    from .collection import BulkCoolerType, OnFarmTankType, CanCollectionType

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

    bulk_cooler: Optional[Annotated["BulkCoolerType", strawberry.lazy(".collection")]]
    on_farm_tank: Optional[Annotated["OnFarmTankType", strawberry.lazy(".collection")]]
    vehicle: Optional[Annotated["VehicleType", strawberry.lazy(".distribution")]]
    sample_type: SampleTypeEnum

@strawberry.type
class MilkTransferType:
    id: int
    source_type: Optional[str]           
    transfer_date: datetime             
    arrival_datetime: Optional[datetime] 
    status: str                          
    total_volume: Optional[float]      
    remarks: Optional[str]             

    vehicle: Optional[Annotated["VehicleType", strawberry.lazy(".distribution")]]
    destination: Optional[Annotated["PlantType", strawberry.lazy(".plants")]]

    departure_weight_kg: Optional[float]
    arrival_weight_kg: Optional[float]

    bulk_cooler: Optional[Annotated["BulkCoolerType", strawberry.lazy(".collection")]]
    on_farm_tank: Optional[Annotated["OnFarmTankType", strawberry.lazy(".collection")]]
    can_collection: Optional[Annotated["CanCollectionType", strawberry.lazy(".collection")]]

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
    bulk_cooler: Optional[Annotated["BulkCoolerType", strawberry.lazy(".collection")]]
    on_farm_tank: Optional[Annotated["OnFarmTankType", strawberry.lazy(".collection")]]
    can_collection: Optional[Annotated["CanCollectionType", strawberry.lazy(".collection")]]

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
class MilkLotVolumeStatType:
    date: date
    status: str
    total_volume: float
