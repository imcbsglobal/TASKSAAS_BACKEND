from django.db import models

class SettingsOptions(models.Model):
    client_id = models.CharField(max_length=100, unique=True)

    order_rate_editable = models.BooleanField(default=False)

    default_price_code = models.CharField(max_length=50, null=True, blank=True)

    protected_price_users = models.JSONField(default=dict)

    # ✅ NEW OPTION
    read_price_category = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "settings_options"

    def __str__(self):
        return self.client_id
