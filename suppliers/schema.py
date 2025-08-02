import strawberry
from strawberry_django import type as strawberry_django_type, field
from suppliers.models import Supplier, MilkLot
from plants.models import Tester
from typing import List
from strawberry.types import Info
from strawberry.permission import BasePermission
from typing import Optional
from decimal import Decimal
from graphql import GraphQLError
from datetime import date

class IsAuthenticated(BasePermission):
    message = "User is not authenticated"

    def has_permission(self, source, info: Info, **kwargs):
        return info.context.request.user.is_authenticated
    


@strawberry_django_type(Supplier)
class SupplierType:
    id: strawberry.auto
    address: strawberry.auto
    phone_number: strawberry.auto
    email: strawberry.auto
    daily_capacity: strawberry.auto
    total_dairy_cows: strawberry.auto
    annual_output: strawberry.auto
    distance_from_plant: strawberry.auto
    aadhar_number: strawberry.auto
    bank_account_number: strawberry.auto
    bank_name: strawberry.auto
    ifsc_code: strawberry.auto


@strawberry.input
class MilkLotInput:
    supplier_id: int
    volume_l: float
    fat_percent: float
    protein_percent: float
    lactose_percent: float
    total_solids: float
    snf: float
    urea_nitrogen: float
    bacterial_count: int

@strawberry.type
class MilkLotType:
    id: int
    supplier_id: int
    volume_l: float
    fat_percent: float
    total_price: Optional[Decimal]
    protein_percent: float
    urea_nitrogen: float
    lactose_percent: float
    total_solids: float
    snf: float
    price_per_litre: Optional[Decimal]
    status: str
    bacterial_count: int
    date_created: Optional[date]

@strawberry.type
class Query:
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
    def milk_lot_by_id(self, info: Info, id: int) -> Optional[MilkLotType]:
        user = info.context.request.user
        try:
            tester = Tester.objects.get(user=user)
            milk_lot = MilkLot.objects.get(id=id, tester=tester)
            return milk_lot
        except Tester.DoesNotExist:
            raise GraphQLError("Supplier profile not found.")
        except MilkLot.DoesNotExist:
            raise GraphQLError(f"Milk Lot with ID {id} not found or not authorized.")
        
    @strawberry.field(permission_classes=[IsAuthenticated])
    def milk_lot_list(self,) -> List[MilkLotType]:
        try:
            milk_lots = MilkLot.objects.all().order_by('-date_created')
            return milk_lots
        except Supplier.DoesNotExist:
            raise GraphQLError("Supplier profile not found.")





@strawberry.type
class Mutation:
    @strawberry.mutation(permission_classes=[IsAuthenticated])
    def create_supplier(
        self,
        info: Info,
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
        user = info.context.request.user

        supplier, created = Supplier.objects.update_or_create(
            user=user,
            defaults={
                'phone_number': phone_number,
                'email': email,
                'daily_capacity': daily_capacity,
                'total_dairy_cows': total_dairy_cows,
                'annual_output': annual_output or 0.0,
                'distance_from_plant': distance_from_plant or 0.0,
                'aadhar_number': aadhar_number,
                'address': address,
                'bank_account_number': bank_account_number,
                'bank_name': bank_name,
                'ifsc_code': ifsc_code,
            }
        )
        return supplier
    
    @strawberry.mutation
    def create_milk_lot(self, info: Info, input: MilkLotInput) -> MilkLotType:
        user = info.context.request.user
        try:
            Tester.objects.get(user=user)
        except Tester.DoesNotExist:
            raise Exception("Tester not found for the authenticated user")
        
        try:
            supplier = Supplier.objects.get(id=input.supplier_id)
        except Supplier.DoesNotExist:
            raise Exception("Supplier not found with the given ID")

        milk_lot,_ = MilkLot.objects.update_or_create(
            supplier=supplier,
            defaults={
                'volume_l': input.volume_l,
                'fat_percent': input.fat_percent,
                'protein_percent': input.protein_percent,
                'lactose_percent': input.lactose_percent,
                'total_solids': input.total_solids,
                'snf': input.snf,
                'urea_nitrogen': input.urea_nitrogen,
                'bacterial_count': input.bacterial_count,
            }
        )

        milk_lot.evaluate_and_price()
        milk_lot.save()

        return MilkLotType(
            id=milk_lot.id,
            supplier_id=supplier.id,
            volume_l=milk_lot.volume_l,
            fat_percent=milk_lot.fat_percent,
            protein_percent=milk_lot.protein_percent,
            lactose_percent=milk_lot.lactose_percent,
            total_solids=milk_lot.total_solids,
            snf=milk_lot.snf,
            urea_nitrogen=milk_lot.urea_nitrogen,
            bacterial_count=milk_lot.bacterial_count,
            total_price=milk_lot.total_price,
            price_per_litre=milk_lot.price_per_litre,
            status=milk_lot.status,
            date_created=milk_lot.date_created,  
        )


schema = strawberry.Schema(query=Query, mutation=Mutation)
