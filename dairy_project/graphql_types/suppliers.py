from typing import Optional

import strawberry
from strawberry_django import type as strawberry_django_type

from suppliers.models import Supplier

from .auth import UserType
from .routes import RouteType

@strawberry.type
class SupplierVolumeStatType:
    supplier_id: int
    supplier_name: str
    status: str
    total_volume: float

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
