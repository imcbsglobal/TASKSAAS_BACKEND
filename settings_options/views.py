from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import jwt

from .models import SettingsOptions
from app1.models import AccPriceCode, AccUser   # ✅ FIXED IMPORT


def decode_jwt_token(request):
    auth_header = request.META.get("HTTP_AUTHORIZATION")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]

    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except Exception:
        return None


@api_view(["GET", "POST"])
def settings_options_api(request):
    payload = decode_jwt_token(request)
    if not payload:
        return Response({"error": "Unauthorized"}, status=401)

    client_id = payload.get("client_id")
    if not client_id:
        return Response({"error": "Invalid token"}, status=401)

    options, _ = SettingsOptions.objects.get_or_create(client_id=client_id)

    # =====================
    # GET
    # =====================
    if request.method == "GET":

        price_codes = list(
            AccPriceCode.objects
            .filter(client_id=client_id)
            .values("code", "name")
        )

        roles = list(
            AccUser.objects
            .filter(client_id=client_id)
            .exclude(role__isnull=True)
            .exclude(role__exact="")
            .values_list("role", flat=True)
            .distinct()
        )

        return Response({
            "client_id": client_id,
            "order_rate_editable": options.order_rate_editable,
            "default_price_codes": options.default_price_codes,
            "protected_price_categories": options.protected_price_categories,
            "price_codes": price_codes,
            "roles": roles
        })

    # =====================
    # POST
    # =====================
    options.order_rate_editable = request.data.get(
        "order_rate_editable",
        options.order_rate_editable
    )
    options.default_price_codes = request.data.get(
        "default_price_codes",
        options.default_price_codes
    )
    options.protected_price_categories = request.data.get(
        "protected_price_categories",
        options.protected_price_categories
    )

    options.save()

    return Response({
        "success": True,
        "client_id": client_id,
        "message": "Settings saved successfully"
    })
