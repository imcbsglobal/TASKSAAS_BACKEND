from django.urls import path
from .views import complete_collection, create_collection, list_collections

urlpatterns = [
    path('create/', create_collection),
    path('list/', list_collections),
    path('complete/', complete_collection),  # ✅ NEW
]
