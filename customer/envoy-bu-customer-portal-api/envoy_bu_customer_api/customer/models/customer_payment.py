from django.db import models

from core_models.core_models import IssuedPolicy, Status


class CustomerPayment(models.Model):

    id = models.BigAutoField(primary_key=True, unique=True,)
    customer_id = models.BigIntegerField(blank=True, null=True)
    policy = models.ForeignKey(
        IssuedPolicy,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    reference_id = models.CharField(max_length=100, unique=True)
    invoice_id = models.BigIntegerField(blank=True, null=True)  
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2)
    outstanding_amount = models.DecimalField(max_digits=12, decimal_places=2)
    receipt =  models.CharField(max_length=100, blank=True, null=True)
    receipt_name =  models.CharField(max_length=100, blank=True, null=True)
    receipt_type =  models.CharField(max_length=100, blank=True, null=True)
    status_id= models.ForeignKey(Status, on_delete=models.SET_NULL, blank=True, null=True,db_column='status_id')  # FK to core_status (e.g. payment_pending)
    status = models.CharField(max_length=100, blank=True, null=True)  # status name from core_status
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
    confirm_receipt =  models.CharField(max_length=100, blank=True, null=True)
    confirm_receipt_name =  models.CharField(max_length=100, blank=True, null=True)
    confirm_receipt_type =  models.CharField(max_length=100, blank=True, null=True)
    customer_payment_id = models.IntegerField(null=True,unique=True,blank=True)



    class Meta:
        db_table = 'cus_payments'

    def __str__(self):
        return f"{self.reference_id} "
