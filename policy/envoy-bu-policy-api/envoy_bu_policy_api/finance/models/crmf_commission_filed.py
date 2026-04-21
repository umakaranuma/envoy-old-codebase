from django.db import models


class CommissionFiled(models.Model):
    """
    Represents commission fields configuration.
    """
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    attribute_name = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=50)
    module = models.CharField(max_length=100)

    class Meta:
        db_table = 'crmf_commission_fields'
        verbose_name = 'Commission Field'
        verbose_name_plural = 'Commission Fields'

    def __str__(self):
        return f"{self.name} - {self.type} ({self.module})"