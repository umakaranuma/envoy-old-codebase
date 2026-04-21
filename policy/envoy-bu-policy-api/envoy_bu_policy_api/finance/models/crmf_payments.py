from django.db import models
from envoy_bu_policy_api.finance.models.crmf_invoices import Invoice

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='finance_payments')
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    outstanding_amount= models.DecimalField(max_digits=12, decimal_places=2)
    entity = models.ForeignKey("core_models.Entity", related_name='finance_payment_entity', on_delete=models.CASCADE,default=1)
    method = models.CharField(max_length=100, blank=True, null=True)
    receipt_number = models.CharField(max_length=100, blank=True, null=True)
    customer_payment_id = models.IntegerField(null=True,unique=True,blank=True)
    reference_id = models.CharField(max_length=255, blank=True, null=True)
    confirmation_payment_receipt_name = models.CharField(max_length=100, blank=True, null=True)
    confirmation_payment_receipt_type = models.CharField(max_length=100, blank=True, null=True)
    confirmation_payment_receipt_url = models.CharField(max_length=100, blank=True, null=True)


    class Meta:
        db_table = "crmf_payments"
        
    def __str__(self):
        return f"Payment for Invoice {self.invoice_id} - Paid: {self.paid_amount}"
