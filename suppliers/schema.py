import strawberry
from strawberry_django import type as strawberry_django_type, field
from distribution.schema import RouteType
from suppliers.models import Supplier, MilkLot, PaymentBill
from plants.models import Tester
from django.contrib.auth.models import User
from typing import List
from strawberry.types import Info
from strawberry.permission import BasePermission
from django.shortcuts import get_object_or_404
from typing import Optional
from decimal import Decimal
from graphql import GraphQLError
from datetime import date, datetime
from distribution.schema import UserType
from collection_center.schema import BulkCoolerType
from plants.schema import TesterType


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
    tester: Optional[TesterType]
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
    last_stirred_at: Optional[datetime]
    created_at: datetime


@strawberry.type
class CanCollectionType:
    id: int
    route: RouteType
    name: str
    total_volume_liters: float
    group_parameter: str
    group_value: float
    group_unit: str
    created_at: datetime


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
    def create_milk_lot(self, info: Info, input: MilkLotInput) -> MilkLotType:
        try:
            tester = Tester.objects.get(id=input.tester_id)
        except Tester.DoesNotExist:
            raise Exception("Tester not found for the authenticated user")

        try:
            supplier = Supplier.objects.get(id=input.supplier_id)
        except Supplier.DoesNotExist:
            raise Exception("Supplier not found with the given ID")

        milk_lot, _ = MilkLot.objects.create(
            supplier=supplier,
            tester=tester,  
            date_created = date.today(),
            defaults={
                "volume_l": input.volume_l,
                "fat_percent": input.fat_percent,
                "protein_percent": input.protein_percent,
                "lactose_percent": input.lactose_percent,
                "total_solids": input.total_solids,
                "snf": input.snf,
                "urea_nitrogen": input.urea_nitrogen,
                "bacterial_count": input.bacterial_count,
                "added_water_percent": input.added_water_percent,
            },
        )

        milk_lot.evaluate_and_price()
        milk_lot.save()

        return MilkLotType(
            id=milk_lot.id,
            tester=tester,
            supplier=supplier,
            volume_l=milk_lot.volume_l,
            fat_percent=milk_lot.fat_percent,
            protein_percent=milk_lot.protein_percent,
            lactose_percent=milk_lot.lactose_percent,
            total_solids=milk_lot.total_solids,
            snf=milk_lot.snf,
            urea_nitrogen=milk_lot.urea_nitrogen,
            bacterial_count=milk_lot.bacterial_count,
            added_water_percent=milk_lot.added_water_percent,
            total_price=milk_lot.total_price,
            price_per_litre=milk_lot.price_per_litre,
            status=milk_lot.status,
            date_created=milk_lot.date_created,
            bill=milk_lot.bill,
            bulk_cooler=milk_lot.bulk_cooler,
            on_farm_tank=milk_lot.on_farm_tank,
            can_collection=milk_lot.can_collection,
        )

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

        return milk_lot

    @strawberry.mutation
    def create_payment_bill(
        self, input: CreatePaymentBillInput
    ) -> CreatePaymentBillPayload:
        try:
            supplier = Supplier.objects.get(id=input.supplier_id)
            payment_date = input.payment_date
            bill_date = input.date

            bill, _ = PaymentBill.objects.update_or_create(
                supplier=supplier,
                date=bill_date,
                defaults={
                    "total_volume_l": 0,
                    "total_value": 0,
                    "is_paid": input.is_paid,
                    "payment_date": payment_date,
                },
            )

            bill.calculate_totals()
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


schema = strawberry.Schema(query=Query, mutation=Mutation)
