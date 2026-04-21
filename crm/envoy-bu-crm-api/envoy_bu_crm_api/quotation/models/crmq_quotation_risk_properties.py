from django.db import models


class RiskProperty(models.Model):
    id = models.AutoField(primary_key=True)
    property_id =  models.BigIntegerField(blank=True, null=True)
    risk_type_id =  models.BigIntegerField(blank=True, null=True)
    quotation_id =  models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = "crmq_quotation_risk_properties"

    def __str__(self):
        return f"Risk Property {self.id}"