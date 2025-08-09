import strawberry
from typing import Optional
from datetime import datetime
from .models import BulkCooler
from strawberry.permission import BasePermission
from strawberry.types import Info
from graphql import GraphQLError
from typing import List
from suppliers.models import MilkLot



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
    last_stirred_at: Optional[datetime]
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
                last_stirred_at=c.last_stirred_at,
                created_at=c.created_at,
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
    ) -> AssignLotsPayload:
        try:
            cooler = BulkCooler.objects.get(id=bulk_cooler_id)
            lots = list(MilkLot.objects.filter(id__in=milk_lot_ids))

            count = cooler.add_lots(*lots)

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