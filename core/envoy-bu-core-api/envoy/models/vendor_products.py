from django.db import models

class VendorProducts(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    code = models.CharField(max_length=100, blank=True, null=True)  
    category_id = models.BigIntegerField(blank=True, null=True)
    vendor_id = models.BigIntegerField(blank=True, null=True)
    coverage_level = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    currency_id = models.BigIntegerField(blank=True, null=True)
    premium_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    deductible_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    claim_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    added_by = models.BigIntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    docs = models.CharField(max_length=255, blank=True, null=True)
    entity_id = models.BigIntegerField(blank=True, null=True)
    

    class Meta:
        db_table = "core_vendor_products"

    def __str__(self):
        return self.name