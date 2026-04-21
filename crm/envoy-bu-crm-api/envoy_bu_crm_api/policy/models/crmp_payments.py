from django.db import models
from envoy_bu_crm_api.policy.models.crmp_request_policy_invoices import RequestPolicyInvoice

class Payment(models.Model):
    invoice = models.ForeignKey(RequestPolicyInvoice, on_delete=models.CASCADE, related_name='payments')
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    outstanding_amount= models.DecimalField(max_digits=12, decimal_places=2)
    entity = models.ForeignKey("sales.Entity", related_name='payment_entity', on_delete=models.CASCADE,default=1)
    method = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        db_table = "crmp_payments"
        
    def __str__(self):
        return f"Payment for Invoice {self.invoice_id} - Paid: {self.paid_amount}"
