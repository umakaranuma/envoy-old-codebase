from django.db import models

class ProductVendorProduct(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    product_id = models.BigIntegerField(null=True, blank=True)
    vendor_product_id = models.BigIntegerField(null=True, blank=True)
   

    class Meta:
        db_table = "core_product_vendor_products"

    def __str__(self):
        return str(self.id)