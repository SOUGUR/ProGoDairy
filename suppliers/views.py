from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def supplier_list(request):
    allowed_groups = ['suppliers']
    if request.user.is_superuser or request.user.groups.filter(name__in=allowed_groups).exists():
        return render(request, "suppliers/supplier_list.html")
    else:
        return render(request, "accounts/error_page.html")


def create_supplier(request):
    return render(request, "suppliers/create_supplier.html")


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

