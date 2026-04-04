from django.db import models

class SettingsOptions(models.Model):
    client_id = models.CharField(max_length=100, unique=True)

    order_rate_editable = models.BooleanField(default=False)

    default_price_code = models.CharField(max_length=50, null=True, blank=True)

    protected_price_users = models.JSONField(default=dict)

    # ✅ REMOTE PUNCH IN
    remote_punchin_users = models.JSONField(default=list, null=True, blank=True)

    # ✅ LOGO OPTION
    logo = models.ImageField(upload_to='client_logos/', null=True, blank=True)

    # ✅ NEW OPTION
    read_price_category = models.BooleanField(default=False)
    barcode_based_list = models.BooleanField(default=False)
    default_print_form = models.CharField(
        max_length=20,
        default="form1"
    )

    tax_type = models.CharField(
        max_length=20,
        default="no_tax"
    )

    user_type = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        default="All"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "settings_options"

    def __str__(self):
        return self.client_id
