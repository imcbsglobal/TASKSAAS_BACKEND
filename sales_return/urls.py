from django.urls import path
from . import views

urlpatterns = [
    path("create", views.create_sales_return),
    path("list", views.sales_return_list),
    path("list-all", views.sales_return_list_all),
    path("status-change", views.sales_return_status_change),
]