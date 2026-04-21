from django.db import models
from .crmf_commission_filed import CommissionFiled


class CommissionFieldValue(models.Model):
    """
    Represents values for commission fields.
    """
    id = models.BigAutoField(primary_key=True)
    commission_field = models.ForeignKey(
        CommissionFiled,
        on_delete=models.CASCADE,
        db_column='commission_field_id'
    )
    value = models.CharField(max_length=255)
    type = models.CharField(max_length=50)
    user_id = models.IntegerField(null=True, blank=True)
    team_id = models.IntegerField(null=True, blank=True)
    commission_setup_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'crmf_commission_field_values'
        verbose_name = 'Commission Field Value'
        verbose_name_plural = 'Commission Field Values'

    def __str__(self):
        return f"{self.commission_field.name}: {self.value} ({self.type})"