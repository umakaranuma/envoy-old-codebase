from django.db import models

class ProductDocumentType(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    name = models.CharField(max_length=255, blank=False, null=False)
    is_mandatory = models.BooleanField(default=False)
    vendor_product_id = models.BigIntegerField(blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    

    class Meta:
        db_table = "core_product_document_types"

    def __str__(self):
        return self.name