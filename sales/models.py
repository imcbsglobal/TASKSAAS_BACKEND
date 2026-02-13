from django.db import models
import uuid

class Sales(models.Model):

    STATUS_CHOICES = [
        ('uploaded to server', 'Uploaded to Server'),
        ('completed', 'Completed'),
    ]

    sales_id = models.CharField(max_length=50, editable=False)

    customer_name = models.CharField(max_length=200)
    customer_code = models.CharField(max_length=100)
    area = models.CharField(max_length=200)

    product_name = models.CharField(max_length=200)
    item_code = models.CharField(max_length=100)
    barcode = models.CharField(max_length=100)

    payment_type = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    client_id = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    remark = models.TextField(blank=True, null=True)

    device_id = models.CharField(max_length=100)

    # ✅ SAME AS ITEM_ORDERS
    status = models.CharField(
        max_length=30,
        choices=STATUS_CHOICES,
        default='uploaded to server'
    )

    status_changed_date = models.DateField(blank=True, null=True)
    status_changed_time = models.TimeField(blank=True, null=True)
    status_changed_by = models.CharField(max_length=100, blank=True, null=True)

    created_date = models.DateField(auto_now_add=True)
    created_time = models.TimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.sales_id:
            self.sales_id = f"SAL-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

    class Meta:
        db_table = "sales"
        ordering = ['-id']
