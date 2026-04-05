from datetime import date, datetime
from typing import List, Optional

import strawberry
import strawberry_django
from strawberry import auto
from strawberry_django import type as strawberry_django_type

from distribution.models import CIPRecord, Distributor, Vehicle

from .auth import UserType
from .routes import RouteType


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

@strawberry.input
class VehicleInput:
    distributor_id: int
    name: str
    vehicle_id: str
    capacity_liters: Optional[float] = None
    route_id: int

@strawberry.input
class SealInput:
    seal_no: str
    position: str

@strawberry.type
class GatePassSealType:
    id: int
    seal_no: str
    position: str

@strawberry.input
class GatePassInput:
    milk_transfer_id: int
    gate_pass_status: str

    empty_tare_kg: float
    net_volume_l: float
    density_kg_per_l: float

    cip_record_id: int
    route_id: Optional[int]
    driver_id: int
    expected_arrival_plant: str

    seals: Optional[List[SealInput]] = None  

@strawberry.type
class GatePassType:
    id: int
    gate_pass_status: str

    created_at: datetime
    issued_at: Optional[datetime]
    completed_at: Optional[datetime]
    route : Optional[RouteType]
    empty_tare_kg: float
    net_volume_l: float
    density_kg_per_l: float
    expected_arrival_plant: datetime

    # ---------------- Related ----------------

    @strawberry.field
    def driver(self) -> Optional[VehicleDriverType]:
        return self.driver

    @strawberry.field
    def vehicle(self) -> Optional[VehicleType]:
        return self.milk_transfer.vehicle if self.milk_transfer else None


    @strawberry.field
    def cip_record(self) -> Optional[CIPRecordType]:
        return self.cip_record

    # ---------------- Seals ----------------

    @strawberry.field
    def seals(self) -> List["GatePassSealType"]:
        return self.seals.all()