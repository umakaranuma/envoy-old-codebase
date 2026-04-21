from django.db import models

class RequestType(models.Model):
    name = models.CharField(max_length=255)  
    description = models.TextField(blank=True, null=True)  

    def __str__(self):
        return self.name

    class Meta:
        db_table = "crmp_request_types"
        
class PaymentPlan(models.Model):
    name = models.CharField(max_length=255)  # Name of the payment plan (e.g., Monthly, Annually)
    description = models.TextField(blank=True, null=True)  
    duration_months = models.IntegerField() 
    def __str__(self):
        return self.name

    class Meta:
        db_table = "crmp_payment_plans"