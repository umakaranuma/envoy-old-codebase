from django.db import models
from envoy_bu_crm_api.policy.models.crmp_request_policies import RequestPolicy

class IssuedPolicy(models.Model):
    # Policy details 
    brokerage_policy_id = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2,blank=True, null=True)
    credit_period_days = models.IntegerField()
    credit_age_days = models.IntegerField()
    insurer_invoice_id = models.CharField(max_length=255, blank=False, null=False)  # Insurer Invoice ID
    insurer_policy_id = models.CharField(max_length=255, blank=True, null=True,)  # Insurer Invoice ID
    sum_insured = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    premium_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    policy_effective_date = models.DateField(blank=True, null=True)
    policy_document = models.URLField(blank=True, null=True) 
    policy_document_name = models.CharField(max_length=255, blank=True, null=True)
    policy_request = models.ForeignKey(RequestPolicy, related_name='policy_req', on_delete=models.CASCADE,blank=True,null=True)
    entity = models.ForeignKey("sales.Entity", related_name='policy_entity', on_delete=models.CASCADE,default=1)
    remarks = models.TextField(blank=True, null=True)
    policy_base=models.ForeignKey("policy.PolicyBase", related_name='policy_issued_base', on_delete=models.CASCADE)
    invoice_document = models.URLField(blank=True, null=True) 
    invoice_document_name = models.CharField(max_length=255, blank=True, null=True)
    initial_premium_amount=models.DecimalField(max_digits=12, decimal_places=2,blank=True, null=True)
  
    class Meta:
        db_table = "crmp_issued_policies"

    def __str__(self):
        return f"Policy {self.brokerage_policy_id}"

