from django.db import transaction
from .models import MilkPaymentInvoice, MilkPaymentInvoiceItem

def create_daily_milk_payment_invoice(supplier, lot_date, created_by=None):

    with transaction.atomic():
        invoice, new = MilkPaymentInvoice.objects.select_for_update().get_or_create(
            supplier=supplier,
            invoice_date=lot_date,
            defaults={
                "invoice_num": f"MLK-{supplier.id}-{lot_date.isoformat()}",
                "created_by": created_by,
            },
        )
        if not new:
            return invoice 

        approved_lots = supplier.lots.filter(
            date_created=lot_date, status="approved"
        ).select_related()

        for lot in approved_lots:
            MilkPaymentInvoiceItem.objects.create(
                invoice=invoice,
                milk_lot=lot,
                qty_l=lot.volume_l,
                price_per_litre=lot.price_per_litre,
                total_price=lot.total_price,
            )

        invoice.recalculate_totals()
        return invoice