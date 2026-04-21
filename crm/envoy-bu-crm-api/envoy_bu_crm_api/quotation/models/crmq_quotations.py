from django.db import models

class Quotation(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=255)
    requested_data = models.DateField()
    customer_id = models.BigIntegerField(null=True)
    status = models.CharField(max_length=255)
    notes = models.CharField(max_length=250, blank=True, null=True)
    request_type = models.CharField(max_length=255, blank=True, null=True)
    opportunity_type_id = models.JSONField(blank=True, null=True)
    opportunity_id = models.BigIntegerField(blank=True, null=True)
    entity_id = models.BigIntegerField(blank=True, null=True)
    email_data = models.JSONField(blank=True, null=True)
    status_id = models.BigIntegerField(blank=True, null=True)


    class Meta:
        db_table = "crmq_quotations"

    def __str__(self):
        return self.code

