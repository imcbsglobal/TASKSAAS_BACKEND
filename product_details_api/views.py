from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Prefetch
from app1.models import AccProduct
from product_details_api.models import AccProductBatch, AccProductPhoto
from product_details_api.serializers import (
    ProductSerializer,
    ProductBatchSerializer,
    ProductPhotoSerializer,
)


@api_view(["GET"])
def get_product_details(request):
    client_id = request.GET.get("client_id")

    if not client_id:
        return Response({"error": "client_id is required"}, status=400)

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

    response_data = []

    for p in products:
        product_data = ProductSerializer(p).data
        product_data["batches"] = ProductBatchSerializer(p.batch_list, many=True).data
        product_data["photos"] = ProductPhotoSerializer(p.photo_list, many=True).data

        response_data.append(product_data)

    return Response({
        "success": True,
        "total": len(response_data),
        "products": response_data
    }, status=200)
