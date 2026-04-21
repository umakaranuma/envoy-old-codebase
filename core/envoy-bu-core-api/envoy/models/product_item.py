from django.db import models

from envoy.models.entity import Entity

class ProductItem(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    entity = models.ForeignKey(
        Entity,
        on_delete=models.RESTRICT,
        related_name="product_items",
        null=True,
        blank=True,
        default=None
    )
    
    class Meta:
        db_table = "core_product_items"

    def __str__(self):
        return f"{self.title}"

