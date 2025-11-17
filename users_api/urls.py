from django.urls import path
from .views import list_users

urlpatterns = [
    path('list/', list_users, name='list_users'),
]