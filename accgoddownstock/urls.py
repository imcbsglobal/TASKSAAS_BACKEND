from django.urls import path
from .views import get_goddown_stock

urlpatterns = [
    path('goddown-stock/', get_goddown_stock, name='get_goddown_stock'),
]