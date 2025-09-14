from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import qrcode
import base64
from io import BytesIO

@login_required
def supplier_list(request):
    allowed_groups = ['suppliers']
    if request.user.is_superuser or request.user.groups.filter(name__in=allowed_groups).exists():
        return render(request, "suppliers/supplier_list.html")
    else:
        return render(request, "accounts/error_page.html")


def create_supplier(request):
    return render(request, "suppliers/create_supplier.html")

def tanker_usage(request):
    return render(request, "suppliers/tanker_usage.html")


def milk_lot_result_list_view(request):
    return render(request, "suppliers/milk_lot_list.html")


def create_milk_lot_view(request):
    return render(request, "suppliers/add_milk_result.html")


def edit_milk_lot(request, lot_id):
    return render(request, "suppliers/add_milk_result.html", {"lot_id": lot_id})


def on_farm_bulk_pooling(request):
    return render(request, "suppliers/on_farm_bulk_pooling.html")

def canCollection(request):
    return render(request, "suppliers/canCollection.html")

def create_payment_bill(request):
    return render(request, "suppliers/payment_bill_list.html")

def view_payment_bill(request,bill_id):
    url = request.build_absolute_uri(f"/bill/{bill_id}/details/")
    qr = qrcode.make(url)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, "suppliers/payment_invoice.html",{"bill_id": bill_id, "qr_code": qr_base64})

def bill_details_view(request, bill_id):
    return render(request, "suppliers/bill_details.html", {"bill_id": bill_id})