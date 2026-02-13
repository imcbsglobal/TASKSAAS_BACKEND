from django.urls import path
from . import views

urlpatterns = [
    path("create", views.create_sales, name="create_sales"),
    path("list", views.sales_list, name="sales_list"),
    path("list-all", views.sales_list_all, name="sales_list_all"),
    path("status-change", views.change_sales_status, name="change_sales_status"),
]
