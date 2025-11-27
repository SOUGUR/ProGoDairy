import strawberry
from datetime import date
from typing import Optional

@strawberry.type
class BillSummaryType:
    is_paid: bool
    total_value: float
    total_volume_l: float

@strawberry.type
class PaymentBillType:
    id: int
    total_volume_l: float
    total_value: float
    is_paid: bool
    payment_date: Optional[date] = None

@strawberry.type
class InvoiceType:
    supplier_name: str
    route_name: Optional[str]
    last_supply_date: date
    total_due: float
    amount_paid: float
    status: str
