from django.db import models



class ProductCategory(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False,null=False)
    title = models.CharField(max_length=255, blank=False, null=False)
    description = models.CharField(max_length=255, blank=True, null=True)
    code = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_product_categories"
        
    def __str__(self):
        return self.title