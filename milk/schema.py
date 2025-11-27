from datetime import datetime
from typing import List, Optional

import strawberry
from django.core.exceptions import ObjectDoesNotExist

from collection_center.models import BulkCooler
from dairy_project.graphql_types.collection import UpdateTankerInput, UpdateTankerResponse
from dairy_project.graphql_types.milk import (
    CompositeSampleInput,
    CompositeSampleType,
    MilkPricingConfigInput,
    MilkPricingConfigType,
    UpdateCompositeSampleInput,
)
from distribution.models import Route, Vehicle
from milk.models import MilkPricingConfig
from suppliers.models import OnFarmTank

from .models import CompositeSample





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
        qs = CompositeSample.objects.all().order_by('-collected_at')

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
    
    @strawberry.field
    def milk_pricing_config(self, route_id: int) -> Optional[MilkPricingConfigType]:
        try:
            return MilkPricingConfig.objects.get(route_id=route_id)
        except MilkPricingConfig.DoesNotExist:
            return None
    
    
@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_composite_sample(self, input: CompositeSampleInput) -> CompositeSampleType:
        print(input)
        bulk_cooler = BulkCooler.objects.filter(id=input.bulk_cooler_id).first() if input.bulk_cooler_id else None
        on_farm_tank = OnFarmTank.objects.filter(id=input.on_farm_tank_id).first() if input.on_farm_tank_id else None
        vehicle = Vehicle.objects.filter(vehicle_id=input.vehicle_id).first() if input.vehicle_id else None
        if not (bulk_cooler or on_farm_tank or vehicle):
            raise ValueError("At least one of bulk_cooler_id, on_farm_tank_id, or vehicle_id must be provided.")
        
        if bulk_cooler is not None:
            bulk_cooler.is_stirred = input.is_stirred
            bulk_cooler.save(update_fields=["is_stirred"])

        if on_farm_tank is not None:
            on_farm_tank.is_stirred = input.is_stirred
            on_farm_tank.save(update_fields=["is_stirred"])
        
        if not bulk_cooler and not on_farm_tank:
            sample_type_value = 'instant-gate tests'
        else:
            sample_type_value = 'society test'


        sample = CompositeSample.objects.create(
            bulk_cooler=bulk_cooler,
            on_farm_tank=on_farm_tank,
            vehicle=vehicle,
            remark=input.remark,
            sample_volume_ml=input.sample_volume_ml or 50,
            temperature_c=input.temperature_c or 4.0,
            sample_type=sample_type_value
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
            sample_type=sample.sample_type
        )
    
    @strawberry.mutation
    def update_composite_sample(self, input: UpdateCompositeSampleInput) -> CompositeSampleType:
        try:
            sample = CompositeSample.objects.get(id=input.id)
        except CompositeSample.DoesNotExist:
            raise ValueError("Sample not found")
        for field, value in input.__dict__.items():
            if value is not None and field != "id":
                setattr(sample, field, value)

        sample.save()

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

            cob_test=sample.cob_test,
            alcohol_test=sample.alcohol_test,
            ph_value=sample.ph_value,
            mbtr_quick=sample.mbtr_quick,

            bulk_cooler=sample.bulk_cooler,
            on_farm_tank=sample.on_farm_tank,
            vehicle=sample.vehicle,
            sample_type=sample.sample_type
        )
    
    @strawberry.mutation
    def update_tanker(self, input: UpdateTankerInput) -> UpdateTankerResponse:
        model = None
        if input.type == "bulk_cooler":
            model = BulkCooler
        elif input.type == "on_farm_tank":
            model = OnFarmTank
        else:
            return UpdateTankerResponse(success=False, message="Invalid type. Must be 'bulk_cooler' or 'on_farm_tank'.")

        try:
            tanker = model.objects.get(id=input.id)
        except ObjectDoesNotExist:
            return UpdateTankerResponse(success=False, message=f"{input.type.replace('_',' ').title()} with ID {input.id} not found.")

        updated = False
        if input.last_cleaned_at is not None:
            tanker.last_cleaned_at = input.last_cleaned_at
            updated = True
        if input.last_sanitized_at is not None:
            tanker.last_sanitized_at = input.last_sanitized_at
            updated = True
        if input.service_interval_days is not None:
            tanker.service_interval_days = input.service_interval_days
            updated = True
        if input.last_serviced_at is not None:
            tanker.last_serviced_at = input.last_serviced_at
            updated = True
        if input.last_calibration_date is not None:
            tanker.last_calibration_date = input.last_calibration_date
            updated = True

        if not updated:
            return UpdateTankerResponse(success=False, message="No fields provided to update.")

        tanker.save()
        return UpdateTankerResponse(success=True, message=f"{input.type.replace('_',' ').title()} with ID {input.id} updated successfully.")
    
    @strawberry.mutation
    def update_milk_pricing_config(self, info, input: MilkPricingConfigInput) -> MilkPricingConfigType:
        route = Route.objects.get(id=input.routeId)
        config, _ = MilkPricingConfig.objects.get_or_create(route=route)
        for field, value in input.__dict__.items():
            if value is not None:
                setattr(config, field, value)
        config.save()
        return config

schema = strawberry.Schema(query=Query, mutation=Mutation)

