from django.urls import path
from . import views

urlpatterns = [
    path("create", views.create_item_order, name="create_item_order"),
    path("list", views.item_orders_list, name="item_orders_list"),
]