import strawberry
from typing import Optional
from datetime import datetime
from collection_center.schema import BulkCoolerType
from distribution.schema import VehicleType
from suppliers.schema import OnFarmTankType
from suppliers.models import OnFarmTank
from collection_center.models import BulkCooler
from distribution.models import Vehicle
from .models import CompositeSample
from typing import List


@strawberry.input
class CompositeSampleInput:
    bulk_cooler_id: Optional[int] = None
    on_farm_tank_id: Optional[int] = None
    vehicle_id: Optional[int] = None
    remark: Optional[str] = None
    sample_volume_ml: Optional[int] = 50
    temperature_c: Optional[float] = 4.0


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
    passed: Optional[bool]

    bulk_cooler: Optional["BulkCoolerType"]
    on_farm_tank: Optional["OnFarmTankType"]
    vehicle: Optional["VehicleType"]


@strawberry.type
class Query:
    @strawberry.field
    def composite_samples(
        self,
        info,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source_type: Optional[str] = None,  
        status: Optional[str] = None,     
    ) -> List[CompositeSampleType]:
        qs = CompositeSample.objects.all()

        if start_date:
            qs = qs.filter(collected_at__gte=start_date)
        if end_date:
            qs = qs.filter(collected_at__lte=end_date)
        if source_type == "bulk_cooler":
            qs = qs.filter(bulk_cooler__isnull=False)
        elif source_type == "on_farm_tank":
            qs = qs.filter(on_farm_tank__isnull=False)
        elif source_type == "can_collection":
            qs = qs.filter(vehicle__isnull=False)
        if status:
            qs = qs.filter(passed=status)

        return qs
    
    
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_composite_sample(self, input: CompositeSampleInput) -> CompositeSampleType:
        bulk_cooler = BulkCooler.objects.filter(id=input.bulk_cooler_id).first() if input.bulk_cooler_id else None
        on_farm_tank = OnFarmTank.objects.filter(id=input.on_farm_tank_id).first() if input.on_farm_tank_id else None
        vehicle = Vehicle.objects.filter(id=input.vehicle_id).first() if input.vehicle_id else None

        if not (bulk_cooler or on_farm_tank or vehicle):
            raise ValueError("At least one of bulk_cooler_id, on_farm_tank_id, or vehicle_id must be provided.")

        sample = CompositeSample.objects.create(
            bulk_cooler=bulk_cooler,
            on_farm_tank=on_farm_tank,
            vehicle=vehicle,
            remark=input.remark,
            sample_volume_ml=input.sample_volume_ml or 50,
            temperature_c=input.temperature_c or 4.0,
        )

        return CompositeSampleType(
            id=sample.id,
            sample_volume_ml=sample.sample_volume_ml,
            collected_at=sample.collected_at,
            temperature_c=sample.temperature_c,
            received_at_lab=sample.received_at_lab,
            remark=sample.remark,

            fat_percent=sample.fat_percent,
            snf_percent=sample.snf_percent,
            protein_percent=sample.protein_percent,
            bacterial_count=sample.bacterial_count,
            antibiotic_residue=sample.antibiotic_residue,
            added_water_percent=sample.added_water_percent,
            passed=sample.passed,

            bulk_cooler=sample.bulk_cooler,
            on_farm_tank=sample.on_farm_tank,
            vehicle=sample.vehicle,
        )
    

schema = strawberry.Schema(query=Query, mutation=Mutation)

