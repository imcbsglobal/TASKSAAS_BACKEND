from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Prefetch
import jwt
from django.conf import settings

from app1.models import AccProduct
from product_details_api.models import AccProductBatch, AccProductPhoto
from product_details_api.serializers import (
    ProductSerializer,
    ProductBatchSerializer,
    ProductPhotoSerializer,
)


@api_view(["GET"])
def get_product_details(request):

    # 🔐 Validate Token
    auth_header = request.META.get('HTTP_AUTHORIZATION')
    if not auth_header or not auth_header.startswith("Bearer "):
        return Response({"success": False, "error": "Missing or invalid authorization header"}, status=401)

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        client_id = payload.get("client_id")
        if not client_id:
            return Response({"success": False, "error": "Invalid token: Missing client_id"}, status=401)
    except jwt.ExpiredSignatureError:
        return Response({"success": False, "error": "Token expired"}, status=401)
    except jwt.InvalidTokenError:
        return Response({"success": False, "error": "Invalid token"}, status=401)

    # 🚀 Optimized Data Fetch (only logged user's client data)
    products = AccProduct.objects.filter(
        client_id=client_id,
        defected="O"
    ).prefetch_related(
        Prefetch(
            'batches',
            queryset=AccProductBatch.objects.filter(client_id=client_id),
            to_attr='batch_list'
        ),
        Prefetch(
            'photos',
            queryset=AccProductPhoto.objects.filter(client_id=client_id),
            to_attr='photo_list'
        )
    )

    result = []
    for p in products:
        data = ProductSerializer(p).data
        data["batches"] = ProductBatchSerializer(p.batch_list, many=True).data
        data["photos"] = ProductPhotoSerializer(p.photo_list, many=True).data
        result.append(data)

    return Response({
        "success": True,
        "total": len(result),
        "products": result
    }, status=200)
