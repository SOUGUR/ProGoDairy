from django.shortcuts import render

def supplier_list(request):
    return render(request, "suppliers/supplier_list.html")


def create_supplier(request):
    return render(request, "suppliers/create_supplier.html")


def milk_lot_result_list_view(request):
    return render(request, "suppliers/milk_lot_list.html")


def create_milk_lot_view(request):
    return render(request, "suppliers/add_milk_result.html")


def edit_milk_lot(request, lot_id):
    return render(request, "suppliers/add_milk_result.html", {"lot_id": lot_id})


def create_payment_bill(request):
    return render(request, "suppliers/payment_bill_list.html")

