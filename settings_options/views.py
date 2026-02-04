from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework.response import Response
import jwt

from django.db import connection
from .models import SettingsOptions


# =========================
# Decode JWT
# =========================
def decode_jwt_token(request):
    auth_header = request.META.get("HTTP_AUTHORIZATION")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.split(" ")[1]

    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except Exception as e:
        print("JWT ERROR:", e)
        return None


# =========================
# Settings Options API
# =========================
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

        # -------- PRICE CODES --------
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT code, name
                    FROM acc_pricecode
                    WHERE client_id = %s
                    ORDER BY name
                """, [client_id])

                price_codes = [
                    {"code": row[0], "name": row[1]}
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            print("PRICE CODE ERROR:", e)
            price_codes = []

        # -------- USERS (id = username, include role) --------
        try:
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT id, role
                    FROM acc_users
                    WHERE client_id = %s
                    ORDER BY id
                """, [client_id])

                users = [
                    {
                        "id": row[0],
                        "username": row[0],     # id itself is username
                        "role": row[1]          # role from DB
                    }
                    for row in cursor.fetchall()
                ]
        except Exception as e:
            print("USER ERROR:", e)
            users = []

        return Response({
            "client_id": client_id,
            "order_rate_editable": options.order_rate_editable,
            "read_price_category": options.read_price_category,
            "barcode_based_list": options.barcode_based_list,
            "default_price_code": options.default_price_code,
            "protected_price_users": options.protected_price_users,
            "price_codes": price_codes,
            "users": users
        })

    # =====================
    # POST
    # =====================
    try:
        options.order_rate_editable = request.data.get(
            "order_rate_editable",
            options.order_rate_editable
        )

        options.read_price_category = request.data.get(
            "read_price_category",
            options.read_price_category
        )

        options.default_price_code = request.data.get(
            "default_price_code",
            options.default_price_code
        )

        options.protected_price_users = request.data.get(
            "protected_price_users",
            options.protected_price_users
        )

        options.save()

        return Response({
            "success": True,
            "message": "Settings saved successfully"
        })

    except Exception as e:
        print("SAVE ERROR:", e)
        return Response(
            {"error": "Failed to save settings"},
            status=500
        )
