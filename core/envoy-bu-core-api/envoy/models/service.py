from django.db import models

class Service(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200, unique=True)
    fee = models.DecimalField(
        max_digits=20, decimal_places=2, null=True, blank=True, default=0.00)
    description = models.CharField(max_length=250, null=True, blank=True)
    type = models.CharField(
        max_length=50, null=True, blank=True,)
    module = models.CharField(
        max_length=50, null=True, blank=True,)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "core_services"
        
    def __str__(self):
        return self.title