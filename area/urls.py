from django.urls import path
from .views import get_area_list

urlpatterns = [
    path('list/', get_area_list, name='get_area_list'),
]
