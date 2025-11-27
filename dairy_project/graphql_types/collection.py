from datetime import datetime
from typing import TYPE_CHECKING, Annotated, List, Optional

import strawberry

from collection_center.models import BulkCooler
from suppliers.models import MilkLot, OnFarmTank

from .routes import RouteType
from .suppliers import SupplierType

if TYPE_CHECKING:
    from .milk import MilkLotType, MilkTransferType

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
    def milk_lots(self) -> List[Annotated["MilkLotType", strawberry.lazy(".milk")]]:
        return MilkLot.objects.filter(on_farm_tank_id=self.id)
    @strawberry.field
    def related_milk_transfers(self, info) -> List[Annotated["MilkTransferType", strawberry.lazy(".milk")]]:
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
    def milk_lots(self) -> List[Annotated["MilkLotType", strawberry.lazy(".milk")]]:
        return MilkLot.objects.filter(bulk_cooler_id=self.id)
    @strawberry.field
    def related_milk_transfers(self, info) -> List[Annotated["MilkTransferType", strawberry.lazy(".milk")]]:
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
