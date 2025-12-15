from django.urls import path
from .views import create_collection, list_collections

urlpatterns = [
    path('create/', create_collection),
    path('list/', list_collections),
]
