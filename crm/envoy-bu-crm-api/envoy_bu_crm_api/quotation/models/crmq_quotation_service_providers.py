from django.db import models


class QuotationServiceProvider(models.Model):
    id = models.AutoField(primary_key=True)
    quotation_id =  models.BigIntegerField(blank=True, null=True) 
    service_provider_id =  models.BigIntegerField(blank=True, null=True)
    is_received = models.BooleanField(default=False)
    is_shortlisted = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    version = models.CharField(max_length=20, default="1.0")
    opportunity_id = models.BigIntegerField(blank=True, null=True)
    status = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = "crmq_quotation_service_providers"

    def __str__(self):
        return self.quotation_id