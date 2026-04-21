from django.db import models


class CoreSalesTarget(models.Model):

    id = models.AutoField(primary_key=True, unique=True)
    month = models.CharField(max_length=20, blank=False, null=False)
    year = models.IntegerField(blank=False, null=False)
    year_target_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    month_target_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True)
    month_actual_sales_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, default=None)
    year_actual_sales_amount = models.DecimalField(max_digits=20, decimal_places=2, null=True, blank=True, default=None)
    currency = models.CharField(max_length=5, default=None, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey("envoy.User", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "core_sales_targets"

    def __str__(self):
        return f"{self.month} {self.year} - Target: {self.year_target_amount} {self.currency}"
