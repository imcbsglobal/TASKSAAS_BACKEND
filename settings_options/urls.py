from django.urls import path
from .views import settings_options_api

urlpatterns = [
    path("options/", settings_options_api),
]
