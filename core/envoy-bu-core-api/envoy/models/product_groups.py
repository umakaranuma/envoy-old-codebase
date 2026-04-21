from django.db import models
from envoy.models.currency import Currency

class ProductGroup(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name="product_groups" , null=True, blank=True , db_column="currency_id")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "core_product_groups"

    def __str__(self):
        return self.name