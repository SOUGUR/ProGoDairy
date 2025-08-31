import strawberry
import strawberry_django
from strawberry_django import type as strawberry_django_type, field
from suppliers.models import Supplier, MilkLot, PaymentBill, OnFarmTank, CanCollection
from notifications.models import Notification
from django.contrib.auth.models import User
from typing import List
from strawberry.types import Info
from strawberry.permission import BasePermission
from typing import Optional
from decimal import Decimal
from graphql import GraphQLError
from datetime import date, datetime
from accounts.schema import UserType
from distribution.models import Route
from collection_center.schema import BulkCoolerType, AssignLotsPayload
from plants.schema import EmployeeType
from django.core.exceptions import ValidationError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


from accounts.schema import RouteType

class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source, info: Info, **kwargs):
        return info.context.request.user.is_authenticated


@strawberry_django_type(Supplier)
class SupplierType:
    id: int
    user: "UserType"
    address: Optional[str]
    phone_number: Optional[str]
    email: Optional[str]
    daily_capacity: Optional[int]
    total_dairy_cows: Optional[int]
    annual_output: Optional[float]
    distance_from_plant: Optional[float]
    aadhar_number: Optional[str]
    bank_account_number: Optional[str]
    bank_name: Optional[str]
    ifsc_code: Optional[str]
    route: Optional[RouteType]


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


@strawberry.type
class PaymentBillType:
    id: int
    total_volume_l: float
    total_value: float
    is_paid: bool
    payment_date: Optional[date] = None


@strawberry.type
class MilkLotType:
    id: int
    supplier: SupplierType
    tester: Optional[EmployeeType] = strawberry_django.field(field_name="employee")
    volume_l: float
    fat_percent: float
    protein_percent: float
    lactose_percent: float
    total_solids: float
    snf: float
    urea_nitrogen: float
    bacterial_count: int
    added_water_percent: Optional[float]
    price_per_litre: Optional[Decimal]
    total_price: Optional[Decimal]
    status: str
    date_created: Optional[date]
    bill: Optional[PaymentBillType]
    bulk_cooler: Optional["BulkCoolerType"]
    on_farm_tank: Optional["OnFarmTankType"]
    can_collection: Optional["CanCollectionType"]


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
    def approved_milk_lot_list(self) -> List[MilkLotType]:
        try:
            milk_lots = (
                MilkLot.objects.select_related("supplier", "bill")
                .filter(status="approved")
                .order_by("-date_created")
            )
            return milk_lots
        except Supplier.DoesNotExist:
            raise GraphQLError("Supplier profile not found.")
        
    @strawberry.field(permission_classes=[IsAuthenticated])
    def approved_milk_lot_list_by_supplier(self, supplier_id: int) -> List[MilkLotType]:
        milk_lots = (
        MilkLot.objects.select_related("supplier", "bill")
        .filter(supplier_id=supplier_id, status="approved")
        .order_by("-date_created")
    )

        if not milk_lots.exists():
            raise GraphQLError("No approved milk lots found for this supplier.")

        return milk_lots
        
    @strawberry.field
    def on_farm_tanks_by_supplier(self, supplier_id: int) -> List[OnFarmTankType]:
        return OnFarmTank.objects.filter(supplier_id=supplier_id)
    
    @strawberry.field
    def onfarm_tanks_by_route(self, route_id: int) -> List[OnFarmTankType]:
        return OnFarmTank.objects.filter(supplier__route_id=route_id)
    
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

        user = info.context.request.user
        user_name = user.get_full_name()  

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
        
        _ = Notification.objects.create(
            message=f"Milk lot {milk_lot.id} updated by {user_name}."
        )


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
        
schema = strawberry.Schema(query=Query, mutation=Mutation)
