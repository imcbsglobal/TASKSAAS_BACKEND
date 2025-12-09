from rest_framework import serializers
from app1.models import AccProduct
from product_details_api.models import AccProductBatch, AccProductPhoto


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccProduct
        fields = "__all__"


class ProductBatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccProductBatch
        fields = "__all__"


class ProductPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccProductPhoto
        fields = "__all__"
