from django.urls import path

from .views import (bill_details_view, canCollection, create_milk_lot_view,
                    create_payment_bill, create_supplier, edit_milk_lot,
                    milk_lot_result_list_view, on_farm_bulk_pooling,
                    supplier_list, tanker_usage, view_payment_bill)

urlpatterns = [
    path('suppliers/', supplier_list, name='supplier_list'),
    path('suppliers/create/', create_supplier, name='create_supplier'),
    path("milk-lot/create/", create_milk_lot_view, name="create_milk_lot"),
    path("tanker-usage/", tanker_usage, name="tanker_usage"),
    path("milk-lot/list/", milk_lot_result_list_view, name="milk_lot_list"),
    path('milk-lot/edit/<int:lot_id>/', edit_milk_lot, name='edit_milk_lot'),
    path('on_farm_bulk_pooling/', on_farm_bulk_pooling, name='on_farm_bulk_pooling'),
    path('can_collection/', canCollection, name='can_collection'),
    path('create-Payment-Bill/', create_payment_bill, name='create_payment_bill'),
    path("bills/<int:bill_id>/invoice/", view_payment_bill, name="view_payment_bill"),
    path("bill/<int:bill_id>/details/", bill_details_view, name="bill_details_view"),
]
