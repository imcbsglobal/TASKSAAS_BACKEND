from django.urls import path
from .views import get_product_details

urlpatterns = [
    path('get-product-details/', get_product_details),
]