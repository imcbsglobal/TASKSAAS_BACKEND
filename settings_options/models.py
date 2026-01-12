from django.db import models

class SettingsOptions(models.Model):
    client_id = models.CharField(max_length=100, unique=True)

    order_rate_editable = models.BooleanField(default=False)

    default_price_codes = models.JSONField(default=list)

    protected_price_categories = models.JSONField(default=dict)

    class Meta:
        db_table = "settings_options"

    def __str__(self):
        return self.client_id

