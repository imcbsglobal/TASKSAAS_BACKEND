from django.db import models
import uuid

class SalesReturn(models.Model):

    order_id = models.CharField(max_length=50, editable=False)

    customer_name = models.CharField(max_length=200)
    customer_code = models.CharField(max_length=100)
    area = models.CharField(max_length=200)

    product_name = models.CharField(max_length=200)
    item_code = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    product_remark = models.TextField(blank=True, null=True)  # ✅ NEW

    client_id = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    device_id = models.CharField(max_length=100)

    status = models.CharField(
        max_length=30,
        default="uploaded to server"
    )

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)

    class Meta:
        db_table = "sales_return"

