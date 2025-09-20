import strawberry
from typing import List
from strawberry_django import field
from plants.models import Employee, Plant, Silo
from django.db.models import Max
from distribution.models import MilkTransfer
from suppliers.models import MilkLot
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from strawberry.types import Info
from graphql import GraphQLError
from django.utils import timezone
from dairy_project.graphql_types import PlantType, EmployeeType, SiloType, MilkLotVolumeStatType, RouteVolumeStats
from django.db.models import Sum
from datetime import date
import calendar


@strawberry.type
class Query:
    @strawberry.field
    def milk_lot_volume_stats_current_month(self, info) -> list[MilkLotVolumeStatType]:
        today = date.today()
        start_of_month = today.replace(day=1)
        end_of_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])

        qs = (
            MilkLot.objects.filter(date_created__range=[start_of_month, end_of_month])
            .values("date_created", "status")
            .annotate(total_volume=Sum("volume_l"))
            .order_by("date_created")
        )

        return [
            MilkLotVolumeStatType(
                date=row["date_created"],
                status=row["status"],
                total_volume=row["total_volume"] or 0.0,
            )
            for row in qs
        ]
    
    @strawberry.field
    def milk_lot_volume_by_route(self, info) -> List[RouteVolumeStats]:
        today = date.today()

        qs = (
            MilkLot.objects.filter(
                date_created__year=today.year,
                date_created__month=today.month,
            )
            .values("supplier__route__name")
            .annotate(total_volume=Sum("volume_l"))
        )

        return [
            RouteVolumeStats(
                route_name=item["supplier__route__name"] or "Unassigned",
                total_volume=item["total_volume"] or 0
            )
            for item in qs
        ]


    @field
    def testers(self) -> List[EmployeeType]:
        return Employee.objects.filter(role__name="tester")
    
    @field
    def employees(self) -> List[EmployeeType]:
        return Employee.objects.select_related("role", "user").all()

    @strawberry.field
    def plants(self) -> List[PlantType]:
        return Plant.objects.all()
    
    @strawberry.field
    def silos_by_plant(self, info, plant_id: int) -> list[SiloType]:
        try:
            latest_datetime = (
                Silo.objects
                .filter(plant_id=plant_id)
                .aggregate(latest=Max('created_at'))['latest']
            )

            if not latest_datetime:
                return []

            latest_date = latest_datetime.date()


            silos = Silo.objects.filter(
                plant_id=plant_id,
                created_at__date=latest_date
            ).select_related('last_cleaned_by', 'plant').order_by('-created_at')

            return list(silos)

        except Exception as e:
            print(f"Error in silos_by_plant: {e}") 
            return []
    
@strawberry.type
class Mutation:
    @strawberry.mutation
    def assign_silo_to_transfer(
        self,
        info: Info,
        milk_transfer_id: int,
        silo_id: int
    ) -> str:
        try:
            transfer = MilkTransfer.objects.get(pk=milk_transfer_id)
            silo = Silo.objects.get(pk=silo_id)

            transfer.silo = silo

            transfer.save()

            transfer.emptied_at = timezone.now()
            transfer.save(update_fields=["emptied_at"])
            silo.update_transfer_count()
            return f"Silo '{silo.name}' assigned to transfer {transfer.id}. Current silo volume: {silo.current_volume}L"

        except ObjectDoesNotExist as e:
            raise GraphQLError(f"Not found: {str(e)}")

        except ValidationError as e:
            raise GraphQLError(f"Validation error: {e.message_dict if hasattr(e, 'message_dict') else e.messages}")

        except Exception as e:
            raise GraphQLError(f"Unexpected error: {str(e)}")

schema = strawberry.Schema(query=Query, mutation = Mutation)
