from django.urls import path
from .views import create_supplier, supplier_list, create_milk_lot_view,milk_lot_result_list_view, edit_milk_lot_view

urlpatterns = [
    path('suppliers/', supplier_list, name='supplier_list'),
    path('suppliers/create/', create_supplier, name='create_supplier'),
    path("milk-lot/create/", create_milk_lot_view, name="create_milk_lot"),
    path("milk-lot/list/", milk_lot_result_list_view, name="milk_lot_list"),
    path('milk-lot/edit/<int:lot_id>/', edit_milk_lot_view, name='edit_milk_lot'),

]
