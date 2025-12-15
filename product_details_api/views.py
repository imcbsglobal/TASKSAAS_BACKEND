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
    auth_header = request.META.get("HTTP_AUTHORIZATION")
    if not auth_header or not auth_header.startswith("Bearer "):
        return Response({"success": False, "error": "Authorization required"}, status=401)

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        client_id = payload.get("client_id")
    except Exception:
        return Response({"success": False, "error": "Invalid token"}, status=401)

    # ---------- PRICE CODES ----------
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

    # ---------- PRODUCTS ----------
    products = list(
        AccProduct.objects.filter(
            client_id=client_id,
            defected="O"
        ).prefetch_related(
            Prefetch(
                "batches",
                queryset=AccProductBatch.objects.filter(client_id=client_id),
                to_attr="batch_list"
            )
        )
    )

    product_codes = [p.code for p in products]

    # ---------- GODDOWNS ----------
    goddown_map = dict(
        AccGoddown.objects.filter(client_id=client_id)
        .values_list("goddownid", "name")
    )

    stock_map = {}
    for s in AccGoddownStock.objects.filter(
        client_id=client_id,
        product__in=product_codes
    ):
        stock_map.setdefault(s.product, []).append(s)

    # ---------- PHOTOS ----------
    photo_map = {}
    for ph in AccProductPhoto.objects.filter(
        client_id=client_id,
        code__in=product_codes
    ):
        photo_map.setdefault(ph.code, []).append(ph)

    # ---------- RESPONSE ----------
    result = []

    for product in products:
        pdata = ProductSerializer(product).data

        # Batches
        batches = []
        for b in product.batch_list:
            bdata = ProductBatchSerializer(b).data
            transformed = {}

            for field, value in bdata.items():
                if field in price_map and value is not None:
                    transformed[price_codes.get(price_map[field], field)] = value
                else:
                    transformed[field] = value

            batches.append(transformed)

        pdata["batches"] = batches

        # Photos
        pdata["photos"] = ProductPhotoSerializer(
            photo_map.get(product.code, []),
            many=True
        ).data

        # Goddowns
        pdata["goddowns"] = [
            {
                "goddown_id": s.goddownid,
                "goddown_name": goddown_map.get(s.goddownid),
                "quantity": float(s.quantity or 0),
            }
            for s in stock_map.get(product.code, [])
        ]

        result.append(pdata)

    return Response(
        {"success": True, "total": len(result), "products": result},
        status=200
    )
