from django.db import models

class Product(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=255, blank=False, null=False)
    code = models.CharField(max_length=100, unique=False, blank=False, null=False)  # Unique
    category_id = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "core_products"

    def __str__(self):
        return self.name
