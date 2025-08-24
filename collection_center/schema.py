import strawberry
from typing import Optional
from datetime import datetime
from .models import BulkCooler
from strawberry.permission import BasePermission
from strawberry.types import Info
from graphql import GraphQLError
from typing import List
from suppliers.models import MilkLot
from accounts.schema import RouteType




class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source, info: Info, **kwargs):
        return info.context.request.user.is_authenticated

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

@strawberry.type
class AssignLotsPayload:
    success: bool
    message: str

@strawberry.type
class Query:
    @strawberry.field
    def bulk_coolers_by_route(self, route_id: int) -> list[BulkCoolerType]:
        coolers = BulkCooler.objects.filter(route_id=route_id)
        return [
            BulkCoolerType(
                id=c.id,
                name=c.name,
                capacity_liters=c.capacity_liters,
                current_volume_liters=c.current_volume_liters,
                temperature_celsius=c.temperature_celsius,
                last_calibration_date=c.last_calibration_date,
                created_at=c.created_at,
                route=c.route, 
                filled_at=c.filled_at,
                emptied_at=c.emptied_at,
                last_cleaned_at=c.last_cleaned_at,
                last_sanitized_at=c.last_sanitized_at,
                service_interval_days=c.service_interval_days,
                last_serviced_at=c.last_serviced_at,
                        )
            for c in coolers
        ]
    
@strawberry.type
class Mutation:
    @strawberry.mutation
    def assign_milk_lots_to_cooler(
        self,
        bulk_cooler_id: int,
        milk_lot_ids: List[int],
        temperature_celsius: float,
        last_cleaned_at: Optional[datetime] = None,
        last_sanitized_at: Optional[datetime] = None,
        last_calibration_date: Optional[datetime] = None,
        service_interval_days: Optional[int] = None,
        last_serviced_at: Optional[datetime] = None,
    ) -> AssignLotsPayload:
        try:
            cooler = BulkCooler.objects.get(id=bulk_cooler_id)
            lots = list(MilkLot.objects.filter(id__in=milk_lot_ids))


            count = cooler.add_lots(*lots)
            cooler.temperature_celsius = temperature_celsius
            if last_cleaned_at:
                cooler.last_cleaned_at = last_cleaned_at
            if last_sanitized_at:
                cooler.last_sanitized_at = last_sanitized_at
            if last_calibration_date:
                cooler.last_calibration_date = last_calibration_date
            if service_interval_days is not None:
                cooler.service_interval_days = service_interval_days
            if last_serviced_at:
                cooler.last_serviced_at = last_serviced_at

            cooler.save()

            return AssignLotsPayload(
                success=True,
                message=f"{count} milk lots assigned to cooler {cooler.name}",
            )
        except BulkCooler.DoesNotExist:
            raise GraphQLError("Cooler not found")
        except ValueError as e:
            raise GraphQLError(str(e))
        except Exception as e:
            raise GraphQLError(f"Error assigning lots: {e}")



schema = strawberry.Schema(query=Query, mutation=Mutation)