from typing import Annotated, List, TYPE_CHECKING

import strawberry
import strawberry_django
from strawberry_django import type as strawberry_django_type

from plants.models import Silo

if TYPE_CHECKING:
    from .milk import MilkTransferType

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
    @strawberry.field
    def completed_transfers(self) -> List[Annotated["MilkTransferType", strawberry.lazy(".milk")]]:
        return self.incoming_transfers.filter(status="completed")
