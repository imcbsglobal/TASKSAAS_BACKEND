from django.urls import path
from .views import settings_options_api, developer_options_api, logo_api, bank_qr_api

urlpatterns = [
    path("options/", settings_options_api),
    path("developer-options/", developer_options_api),
    path("logo/", logo_api),
    path("bank-qr/", bank_qr_api),
]
