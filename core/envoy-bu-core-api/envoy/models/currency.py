from django.db import models

class Currency(models.Model):
    id = models.AutoField(primary_key=True, unique=True,blank=False,null=False)
    symbol = models.CharField(max_length=10, blank=False, null=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    decimal_digits = models.IntegerField(blank=False, null=False)
    rounding = models.IntegerField(blank=False, null=False)
    code = models.CharField(max_length=100, unique=True, blank=False, null=False)  # Unique

    class Meta:
        db_table = "core_currencies"

    def __str__(self):
        return f"{self.name} ({self.symbol})"
