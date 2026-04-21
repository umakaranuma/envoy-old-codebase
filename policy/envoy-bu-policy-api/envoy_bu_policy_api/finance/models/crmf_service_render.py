from django.db import models

class ServiceRender(models.Model):
    """
    Model for CRMF Services Rendered tracking invoices and payments for services
    """
    id = models.AutoField(primary_key=True)
    invoice_number = models.CharField(max_length=50, null=True, blank=True)
    customer_id = models.BigIntegerField(null=True, blank=True)
    user_id = models.BigIntegerField(null=True, blank=True)
    service_id = models.BigIntegerField(null=True, blank=True)
    service_date = models.DateField()
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    invoice_status = models.BigIntegerField(null=True, blank=True)
    payment_status = models.BigIntegerField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    entity_id = models.BigIntegerField(null=True, blank=True)

    class Meta:
        db_table = 'crmf_services_renders'
        verbose_name = 'Service Rendered'
        verbose_name_plural = 'Services Rendered'

    def __str__(self):
        return