import strawberry
from typing import Optional
from datetime import datetime, date
from .models import BulkCooler
from strawberry.permission import BasePermission
from strawberry.types import Info
from graphql import GraphQLError
from typing import List
from suppliers.models import MilkLot
from dairy_project.graphql_types import BulkCoolerType
from django.db.models import Max
from django.utils.timezone import make_aware


class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source, info: Info, **kwargs):
        return info.context.request.user.is_authenticated



@strawberry.type
class AssignLotsPayload:
    success: bool
    message: str

@strawberry.type
class Query:
    @strawberry.field
    def bulk_coolers_by_route(self, route_id: int) -> list[BulkCoolerType]:
        latest_date = (
        BulkCooler.objects
        .filter(route_id=route_id)
        .aggregate(latest=Max('created_at'))['latest']
    )

        if not latest_date:
            return []

        latest_date_only = latest_date.date()

        coolers = BulkCooler.objects.filter(
            route_id=route_id,
            created_at__date=latest_date_only
        ).order_by('-created_at')

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
                is_stirred = c.is_stirred
            )
            for c in coolers
        ]
    
    @strawberry.field
    def all_bulk_coolers_by_route(
        self,
        route_id: int,
        from_date: date,
        to_date: date
    ) -> List[BulkCoolerType]:
        
        
        from_dt = make_aware(datetime.combine(from_date, datetime.min.time()))
        to_dt = make_aware(datetime.combine(to_date, datetime.max.time()))

        coolers = BulkCooler.objects.filter(
            route_id=route_id,
            created_at__range=(from_dt, to_dt)
        ).order_by("-created_at")

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
                is_stirred=c.is_stirred,
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


    @strawberry.mutation
    def create_bulk_cooler(self, info, cooler_id: int, confirm: bool = False) -> Optional[BulkCoolerType]:
        try:
            original_cooler = BulkCooler.objects.get(id=cooler_id)
        except BulkCooler.DoesNotExist:
            raise Exception("BulkCooler not found")
        
        today = date.today()
        already_exists = BulkCooler.objects.filter(
            name=original_cooler.name,
            created_at__date=today
        ).exists()

        if already_exists:
            raise Exception(
                f"A Bulk Cooler for {original_cooler.name} has already been created today."
            )

        # MAX_AGE_HOURS = 96 

        if original_cooler.last_sanitized_at is None:
            raise Exception(f"Bulk Cooler {original_cooler.name} has no sanitization record.")

        # age = datetime.now(timezone.utc) - original_cooler.last_sanitized_at
        # if age > timedelta(hours=MAX_AGE_HOURS):
        #     if not confirm:
        #         raise Exception(
        #             f"Bulk Cooler {original_cooler.name} was last sanitized {age.days} day(s) ago. "
        #             f"Sanitation must be within {MAX_AGE_HOURS} hours. "
        #             f"Please re-sanitize before use or confirm override."
        #         )
            
        new_cooler = BulkCooler.objects.create(
            route=original_cooler.route,
            name=original_cooler.name,
            capacity_liters=original_cooler.capacity_liters,
            current_volume_liters=0.0,  
            temperature_celsius=original_cooler.temperature_celsius,

            filled_at=None,
            emptied_at=None,

            last_cleaned_at=original_cooler.last_cleaned_at,
            last_sanitized_at=original_cooler.last_sanitized_at,
            last_serviced_at=original_cooler.last_serviced_at,
            last_calibration_date=original_cooler.last_calibration_date,

            service_interval_days=original_cooler.service_interval_days,
        )

        return new_cooler



schema = strawberry.Schema(query=Query, mutation=Mutation)