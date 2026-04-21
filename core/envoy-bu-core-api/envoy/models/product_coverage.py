from django.db import models
from .product_categary import ProductCategory

class ProductCoverage(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    type = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, blank=True, null=True , db_column="type_id")
    description = models.CharField(max_length=255, blank=True, null=True)
    vendor_product_id = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)


    class Meta:
        db_table = "core_product_coverages"

    def __str__(self):
        return self.name