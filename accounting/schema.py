import strawberry
from typing import List, Optional
from datetime import date
from .apis import create_daily_milk_payment_invoice
from suppliers.models import Supplier
from dairy_project.graphql_types import InvoiceType

@strawberry.type
class Query:
    @strawberry.field
    def invoices(
        self,
        info,
        route_id: Optional[int] = None,
        payment_status: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> List[InvoiceType]:

        invoices_list = []
        suppliers = Supplier.objects.all().select_related("route", "user")
        if route_id:
            suppliers = suppliers.filter(route_id=route_id)

        for supplier in suppliers:
            last_lot = (
                supplier.lots.filter(status="approved")
                .order_by("-date_created")
                .first()
            )
            if not last_lot:
                continue 

            lot_date = last_lot.date_created
            if start_date and lot_date < start_date:
                continue
            if end_date and lot_date > end_date:
                continue

            invoice = create_daily_milk_payment_invoice(supplier, lot_date)

            if payment_status and invoice.payment_status != payment_status:
                continue

            total_due = float(invoice.total_value - invoice.total_amount_paid)

            invoices_list.append(
                InvoiceType(
                    supplier_name=supplier.user.username,
                    route_name=supplier.route.name if supplier.route else None,
                    last_supply_date=lot_date,
                    total_due=total_due,
                    amount_paid=float(invoice.total_amount_paid),
                    status=invoice.payment_status.capitalize(),
                )
            )

        return invoices_list