import strawberry
from strawberry_django import field
from suppliers.models import Supplier, MilkLot, PaymentBill, OnFarmTank, CanCollection
from django.contrib.auth.models import User
from typing import List
from strawberry.types import Info
from strawberry.permission import BasePermission
from typing import Optional
from decimal import Decimal
from graphql import GraphQLError
from datetime import date, datetime,timedelta, timezone
from accounts.schema import UserType
from distribution.models import Route
from collection_center.schema import AssignLotsPayload
from django.core.exceptions import ValidationError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Max
from django.utils.timezone import make_aware
from dairy_project.graphql_types import MilkLotType,PaymentBillType, SupplierType,OnFarmTankType, CanCollectionType,AssignCanCollectionPayload

class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source, info: Info, **kwargs):
        return info.context.request.user.is_authenticated



@strawberry.input
class MilkLotInput:
    tester_id: int
    supplier_id: int
    volume_l: float
    fat_percent: float
    protein_percent: float
    lactose_percent: float
    total_solids: float
    snf: float
    urea_nitrogen: float
    bacterial_count: int
    added_water_percent: Optional[float] = 0.0





@strawberry.input
class CreatePaymentBillInput:
    supplier_id: int
    date: str
    is_paid: bool
    payment_date: Optional[str]


@strawberry.type
class CreatePaymentBillPayload:
    success: bool
    bill: Optional[PaymentBillType] = None
    error: Optional[str] = None


@strawberry.django.type(PaymentBill)
class PaymentBillTypeList:
    id: int
    payment_date: Optional[date]
    date: Optional[date]
    total_volume_l: Optional[Decimal]
    total_value: Optional[Decimal]
    is_paid: bool
    pdf_url: Optional[str]
    supplier: SupplierType







@strawberry.type
class Query:
    @strawberry.field(permission_classes=[IsAuthenticated])
    def users(self) -> List[UserType]:
        return User.objects.all()

    @field
    def suppliers(self) -> List[SupplierType]:
        return Supplier.objects.all()

    @strawberry.field(permission_classes=[IsAuthenticated])
    def my_supplier(self, info: Info) -> Optional[SupplierType]:
        user = info.context.request.user
        try:
            return Supplier.objects.get(user=user)
        except Supplier.DoesNotExist:
            return None

    @strawberry.field(permission_classes=[IsAuthenticated])
    def milk_lots_by_bill(self, info: Info, bill_id: int) -> List[MilkLotType]:
        return MilkLot.objects.filter(bill_id=bill_id).select_related(
            "supplier", "bill"
        )

    @strawberry.field(permission_classes=[IsAuthenticated])
    def milk_lot_list(
        self,
    ) -> List[MilkLotType]:
        try:
            milk_lots = MilkLot.objects.select_related("supplier", "bill").order_by(
                "-date_created"
            )
            return milk_lots
        except Supplier.DoesNotExist:
            raise GraphQLError("Supplier profile not found.")

    @strawberry.field(permission_classes=[IsAuthenticated])
    def milk_lot_by_id(self, info: Info, id: int) -> Optional[MilkLotType]:
        try:
            milk_lot = MilkLot.objects.get(id=id)
            return milk_lot
        except MilkLot.DoesNotExist:
            raise GraphQLError(f"Milk Lot with ID {id} not found or not authorized.")

    @strawberry.field(permission_classes=[IsAuthenticated])
    def pending_milk_lot_list(self) -> List[MilkLotType]:
        try:
            milk_lots = (
                MilkLot.objects.select_related("supplier", "bill")
                .filter(status="pending")
                .order_by("-date_created")
            )
            return milk_lots
        except Supplier.DoesNotExist:
            raise GraphQLError("Supplier profile not found.")
        
    @strawberry.field(permission_classes=[IsAuthenticated])
    def pending_milk_lot_list_by_supplier(self, supplier_id: int) -> List[MilkLotType]:
        milk_lots = (
        MilkLot.objects.select_related("supplier", "bill")
        .filter(supplier_id=supplier_id, status="pending")
        .order_by("-date_created")
    )

        if not milk_lots.exists():
            raise GraphQLError("N" \
            "no approved milk lots found for this supplier.")
        return milk_lots
        
    @strawberry.field
    def on_farm_tanks_by_supplier(self, supplier_id: int) -> List[OnFarmTankType]:
        return OnFarmTank.objects.filter(supplier_id=supplier_id)
    
    @strawberry.field
    def onfarm_tanks_by_route(self, route_id: int) -> List[OnFarmTankType]:
        latest_datetime = (
        OnFarmTank.objects
        .filter(supplier__route_id=route_id)
        .aggregate(latest=Max('created_at'))['latest']
    )

        if not latest_datetime:
            return []  

        latest_date = latest_datetime.date()  

        tanks = OnFarmTank.objects.filter(
            supplier__route_id=route_id,
            created_at__date=latest_date  
        ).order_by('-created_at')

        return tanks
    
    @strawberry.field
    def all_onfarm_tanks_by_route(
        self,
        route_id: int,
        from_date: date,
        to_date: date
    ) -> List[OnFarmTankType]:

        from_dt = make_aware(datetime.combine(from_date, datetime.min.time()))
        to_dt = make_aware(datetime.combine(to_date, datetime.max.time()))

        tanks = OnFarmTank.objects.filter(
            supplier__route_id=route_id,
            created_at__range=(from_dt, to_dt)
        ).order_by("-created_at")

        return [
            OnFarmTankType(
                id=t.id,
                name=t.name,
                capacity_liters=t.capacity_liters,
                current_volume_liters=t.current_volume_liters,
                temperature_celsius=t.temperature_celsius,
                last_calibration_date=t.last_calibration_date,
                created_at=t.created_at,
                supplier=t.supplier,
                filled_at=t.filled_at,
                emptied_at=t.emptied_at,
                last_cleaned_at=t.last_cleaned_at,
                last_sanitized_at=t.last_sanitized_at,
                service_interval_days=t.service_interval_days,
                last_serviced_at=t.last_serviced_at,
                is_stirred=t.is_stirred,
            )
            for t in tanks
        ]

    
    @strawberry.field
    def can_collections_by_date(
        self, 
        route_id: int, 
        created_date: date
    ) -> List[CanCollectionType]:
        try:
            route = Route.objects.get(id=route_id)
            collections = CanCollection.objects.filter(
                route=route,
                created_at__date=created_date
            )
            return [
                CanCollectionType(
                    id=c.id,
                    route=c.route,
                    name=c.name,
                    total_volume_liters=c.total_volume_liters,
                    created_at=c.created_at
                )
                for c in collections
            ]
        except Route.DoesNotExist:
            raise GraphQLError("Route not found")

    @field
    def all_payment_bills(self) -> List[PaymentBillTypeList]:
        return PaymentBill.objects.select_related("supplier__user").all()

    @field
    def payment_bill_by_id(self, id: int) -> Optional[PaymentBillTypeList]:
        try:
            return PaymentBill.objects.select_related("supplier__user").get(id=id)
        except PaymentBill.DoesNotExist:
            return None


@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def create_supplier(
        self,
        id: int,
        phone_number: str,
        email: str,
        daily_capacity: float,
        total_dairy_cows: int,
        annual_output: Optional[float] = 0.0,
        distance_from_plant: Optional[float] = None,
        aadhar_number: Optional[str] = None,
        address: Optional[str] = None,
        bank_account_number: Optional[str] = None,
        bank_name: Optional[str] = None,
        ifsc_code: Optional[str] = None,
    ) -> SupplierType:
        user = User.objects.get(id=id)

        supplier, _ = Supplier.objects.update_or_create(
            user=user,
            defaults={
                "phone_number": phone_number,
                "email": email,
                "daily_capacity": daily_capacity,
                "total_dairy_cows": total_dairy_cows,
                "annual_output": annual_output or 0.0,
                "distance_from_plant": distance_from_plant or 0.0,
                "aadhar_number": aadhar_number,
                "address": address,
                "bank_account_number": bank_account_number,
                "bank_name": bank_name,
                "ifsc_code": ifsc_code,
            },
        )
        return supplier

    @strawberry.mutation
    def update_milk_lot(self, info: Info, input: MilkLotInput, lot_id: Optional[int] = None) -> MilkLotType:
        if lot_id:
            try:
                milk_lot = MilkLot.objects.get(id=lot_id)
            except MilkLot.DoesNotExist:
                raise Exception("Milk Lot not found")
        else:
            milk_lot = MilkLot()

        milk_lot.supplier_id = input.supplier_id
        milk_lot.tester_id = input.tester_id
        milk_lot.volume_l = input.volume_l
        milk_lot.fat_percent = input.fat_percent
        milk_lot.protein_percent = input.protein_percent
        milk_lot.lactose_percent = input.lactose_percent
        milk_lot.total_solids = input.total_solids
        milk_lot.snf = input.snf
        milk_lot.urea_nitrogen = input.urea_nitrogen
        milk_lot.bacterial_count = input.bacterial_count
        milk_lot.added_water_percent = input.added_water_percent

        milk_lot.evaluate_and_price()
        milk_lot.save()
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
        "notifications",  
        {
            "type": "send_notification",   
            "message": f"Milk lot {milk_lot.id} was updated successfully!"
        }
        )
        return milk_lot

    @strawberry.mutation
    def create_payment_bill(
        self, input: CreatePaymentBillInput
    ) -> CreatePaymentBillPayload:
        try:
            supplier = Supplier.objects.get(id=input.supplier_id)
            bill_date = input.date
            payment_date = input.payment_date

            approved_lots = MilkLot.objects.filter(
                supplier=supplier, status="approved", date_created=bill_date
            )

            total_volume = sum(lot.volume_l for lot in approved_lots)
            total_value = sum(lot.total_price for lot in approved_lots if lot.total_price)

            if total_volume == 0 or total_value == 0:
                return CreatePaymentBillPayload(
                    success=False,
                    error="No approved milk lots found for this supplier on this date",
                )

            bill, _ = PaymentBill.objects.update_or_create(
                supplier=supplier,
                date=bill_date,
                defaults={
                    "total_volume_l": total_volume,
                    "total_value": total_value,
                    "is_paid": input.is_paid,
                    "payment_date": payment_date,
                },
            )

            approved_lots.update(bill=bill)

            return CreatePaymentBillPayload(
                success=True,
                bill=PaymentBillType(
                    id=bill.id,
                    total_volume_l=bill.total_volume_l,
                    total_value=float(bill.total_value),
                    is_paid=bill.is_paid,
                ),
            )

        except Supplier.DoesNotExist:
            return CreatePaymentBillPayload(success=False, error="Supplier not found")
        except Exception as e:
            return CreatePaymentBillPayload(success=False, error=str(e))



    
    @strawberry.mutation
    def assign_milk_lots_to_onfarm_tank(
        self,
        tank_id: int,
        milk_lot_ids: List[int],
        temperature_celsius: Optional[float] = None,
        last_cleaned_at: Optional[datetime] = None,
        last_sanitized_at: Optional[datetime] = None,
        last_calibration_date: Optional[datetime] = None,
        service_interval_days: Optional[int] = None,
        last_serviced_at: Optional[datetime] = None,
    ) -> AssignLotsPayload:
        try:
            tank = OnFarmTank.objects.get(id=tank_id)
            lots = list(MilkLot.objects.filter(id__in=milk_lot_ids))

            count = tank.add_lots(*lots)

            if temperature_celsius is not None:
                tank.temperature_celsius = temperature_celsius
            if last_cleaned_at:
                tank.last_cleaned_at = last_cleaned_at
            if last_sanitized_at:
                tank.last_sanitized_at = last_sanitized_at
            if last_calibration_date:
                tank.last_calibration_date = last_calibration_date
            if service_interval_days is not None:
                tank.service_interval_days = service_interval_days
            if last_serviced_at:
                tank.last_serviced_at = last_serviced_at

            tank.save()

            return AssignLotsPayload(
                success=True,
                message=f"{count} milk lots assigned to On-Farm Tank {tank.name}",
            )
        except OnFarmTank.DoesNotExist:
            raise GraphQLError("On-Farm Tank not found")
        except ValueError as e:
            raise GraphQLError(str(e))
        except Exception as e:
            raise GraphQLError(f"Error assigning lots: {e}")
        
    @strawberry.mutation
    def assign_milk_lots_to_can_collection(
        self,
        can_collection_id: int,
        milk_lot_ids: List[int],
    ) -> AssignCanCollectionPayload:
        try:
            collection = CanCollection.objects.get(id=can_collection_id)
            lots = list(MilkLot.objects.filter(id__in=milk_lot_ids))

            count = collection.add_lots(*lots)

            return AssignCanCollectionPayload(
                success=True,
                message=f"{count} milk lots assigned to Can Collection {collection.name}",
            )
        except CanCollection.DoesNotExist:
            raise GraphQLError("Can Collection not found")
        except ValidationError as e:
            raise GraphQLError(str(e))
        except Exception as e:
            raise GraphQLError(f"Error assigning lots: {e}")
        
    @strawberry.mutation
    def create_can_collection(
        self,
        route_id: int,
        name: str
    ) -> CanCollectionType:
        try:
            route = Route.objects.get(id=route_id)
            collection = CanCollection.objects.create(
                route=route,
                name=name,
                total_volume_liters=0.0, 
            )
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
            "notifications",  
            {
                "type": "send_notification",   
                "message": f"Can Collection {name} was created successfully!"
            }
            )
            return CanCollectionType(
                id=collection.id,
                route=collection.route,
                name=collection.name,
                total_volume_liters=collection.total_volume_liters,
                created_at=collection.created_at,
            )
        except Route.DoesNotExist:
            raise GraphQLError("Route not found")
        except Exception as e:
            raise GraphQLError(f"Error creating can collection: {e}")
        
    @strawberry.mutation
    def create_onfarm_tank(self, info, tank_id: int, confirm: bool = False) -> Optional[OnFarmTankType]:
        try:
            processed_tank = OnFarmTank.objects.get(id=tank_id)
        except OnFarmTank.DoesNotExist:
            raise Exception("OnFarmTank not found")
        
        today = date.today()
        already_exists = OnFarmTank.objects.filter(
            supplier=processed_tank.supplier,
            name=processed_tank.name,
            created_at__date=today,
        ).exists()

        if already_exists:
            raise Exception(
                f"An On-Farm Tank for {processed_tank.name} has already been created today {today}."
            )

        MAX_AGE_HOURS = 96 

        if processed_tank.last_sanitized_at is None:
            raise Exception(f"Bulk Cooler {processed_tank.name} has no sanitization record.")

        age = datetime.now(timezone.utc) - processed_tank.last_sanitized_at
        if age > timedelta(hours=MAX_AGE_HOURS):
            if not confirm:
                raise Exception(
                    f"Bulk Cooler {processed_tank.name} was last sanitized {age.days} day(s) ago. "
                    f"Sanitation must be within {MAX_AGE_HOURS} hours. "
                    f"Please re-sanitize before use or confirm override."
                )

        new_tank = OnFarmTank.objects.create(
            supplier=processed_tank.supplier,
            name=processed_tank.name,
            capacity_liters=processed_tank.capacity_liters,
            current_volume_liters=0.0, 
            temperature_celsius=processed_tank.temperature_celsius,

            filled_at=None,
            emptied_at=None,

            last_cleaned_at=processed_tank.last_cleaned_at,
            last_sanitized_at=processed_tank.last_sanitized_at,
            last_serviced_at=processed_tank.last_serviced_at,
            last_calibration_date=processed_tank.last_calibration_date,
            service_interval_days=processed_tank.service_interval_days,
        )
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
        "notifications",  
        {
            "type": "send_notification",   
            "message": f"A new OnFarm Tank {today} was created successfully!"
        }
        )
        return new_tank
        
schema = strawberry.Schema(query=Query, mutation=Mutation)
