from decimal import Decimal

import strawberry
from strawberry_django import type as strawberry_django_type

from distribution.models import Route

@strawberry_django_type(Route)
class RouteType:
    id: int
    name: str

@strawberry.type
class RouteVolumeStats:
    route_name: str
    total_volume: Decimal
