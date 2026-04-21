from django.db import models

class ProductGroupProduct(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    product_group_id = models.BigIntegerField(null=True, blank=True)
    product_id = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = "core_product_group_products"

    def __str__(self):
        return str(self.id)