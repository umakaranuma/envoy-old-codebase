from django.db import models


class ServiceRenderPayment(models.Model):
    id = models.AutoField(primary_key=True)
    service_render_id = models.BigIntegerField(null=True, blank=True)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2)
    outstanding_amount = models.DecimalField(max_digits=10, decimal_places=2)
    entity_id = models.BigIntegerField(null=True, blank=True)
    method = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crmf_service_render_payments'
        verbose_name = 'Service Render Payment'
        verbose_name_plural = 'Service Render Payments'
        

    def __str__(self):
        return f"Service Render Payment {self.id} - Payment ID: {self.payment_id}"


