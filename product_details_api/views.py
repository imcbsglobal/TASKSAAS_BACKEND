from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Prefetch
import jwt
from django.conf import settings

from app1.models import AccProduct, AccPriceCode
from product_details_api.models import AccProductBatch, AccProductPhoto
from product_details_api.serializers import (
    ProductSerializer,
    ProductBatchSerializer,
    ProductPhotoSerializer,
)


@api_view(["GET"])
def get_product_details(request):
    # 🔐 Token validation
    auth_header = request.META.get("HTTP_AUTHORIZATION")
    if not auth_header or not auth_header.startswith("Bearer "):
        return Response(
            {"success": False, "error": "Missing or invalid authorization header"},
            status=401
        )

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        client_id = payload.get("client_id")
        if not client_id:
            return Response(
                {"success": False, "error": "Invalid token: Missing client_id"},
                status=401
            )
    except jwt.ExpiredSignatureError:
        return Response({"success": False, "error": "Token expired"}, status=401)
    except jwt.InvalidTokenError:
        return Response({"success": False, "error": "Invalid token"}, status=401)

    # ---------------- PRICE CODES ----------------
    price_codes = dict(
        AccPriceCode.objects.filter(client_id=client_id)
        .values_list("code", "name")
    )

    price_map = {
        "salesprice": "S1",
        "secondprice": "S2",
        "thirdprice": "S3",
        "fourthprice": "S4",
        "nlc1": "S5",
        "bmrp": "MR",
        "cost": "CO",
    }

    # ---------------- LOAD PHOTOS (CORRECT WAY) ----------------
    photo_qs = AccProductPhoto.objects.filter(client_id=client_id)
    photo_map = {}
    for ph in photo_qs:
        key = str(ph.code).strip()
        photo_map.setdefault(key, []).append(ph)

    # ---------------- PRODUCTS ----------------
    products = AccProduct.objects.filter(
        client_id=client_id,
        defected="O"
    ).prefetch_related(
        Prefetch(
            "batches",
            queryset=AccProductBatch.objects.filter(client_id=client_id),
            to_attr="batch_list"
        )
    )

    result = []

    for p in products:
        pdata = ProductSerializer(p).data
        product_code = str(p.code).strip()

        # ---------- BATCHES ----------
        batches = []
        for b in p.batch_list:
            bdata = ProductBatchSerializer(b).data
            transformed = {}

            for field, value in bdata.items():
                if field in price_map and value is not None:
                    price_code = price_map[field]
                    transformed[price_codes.get(price_code, field.upper())] = value
                else:
                    transformed[field] = value

            batches.append(transformed)

        pdata["batches"] = batches

        # ---------- PHOTOS (FIXED) ----------
        pdata["photos"] = ProductPhotoSerializer(
            photo_map.get(product_code, []),
            many=True
        ).data

        result.append(pdata)

    return Response(
        {
            "success": True,
            "total": len(result),
            "products": result
        },
        status=200
    )
