from django.db import models

class SendQuotation(models.Model):
    id = models.AutoField(primary_key=True)
    opportunity_id = models.BigIntegerField(blank=True, null=True)
    entity_id = models.BigIntegerField(blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)
    # selected_attributes = models.JSONField(blank=True, null=True)
    version = models.IntegerField(blank=True, null=True)
    date = models.DateTimeField(blank=True, null=True)
    uploaded_by = models.BigIntegerField(blank=True, null=True)
    quotation_request_id = models.BigIntegerField(blank=True, null=True)
    generated_pdf = models.TextField(blank=True, null=True)
    selected_columns = models.JSONField(null=True, blank=True)  # preferred if using PostgreSQL or modern MySQL
    expiry_date = models.DateField(null=True, blank=True)


    class Meta:
        db_table = 'crmq_send_quotations'
        verbose_name = 'SendQuotation'
        verbose_name_plural = 'SendQuotations'

    def __str__(self):
        return self.id 

