import strawberry
import strawberry_django
from typing import List
from strawberry_django import field
from distribution.schema import UserType

from .models import Tester
@strawberry_django.type(Tester)
class TesterType:
    id: strawberry.auto
    user: UserType
    employee_id: strawberry.auto
    phone_number: strawberry.auto
    address: strawberry.auto
    designation: strawberry.auto
    routes: strawberry.auto


@strawberry.type
class Query:
    @field
    def testers(self) -> List[TesterType]:
        return Tester.objects.all()
    


schema = strawberry.Schema(query=Query)
