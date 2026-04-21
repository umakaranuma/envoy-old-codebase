from django.db import models
from envoy_bu_crm_api.policy.models.crmp_request_type import RequestType, PaymentPlan
from envoy_bu_crm_api.policy.models.crmp_coverage_type import CoverageType

class PolicyBase(models.Model):
    risk_details_form = models.ForeignKey("sales.Form", related_name="request_policy_risk_details", on_delete=models.CASCADE, blank=True, null=True)
    risk_type = models.ForeignKey("sales.OpportunityType", related_name="request_policy_risk_type", on_delete=models.CASCADE, blank=True, null=True)
    insurer = models.ForeignKey("sales.ServiceProvider", related_name="request_policy_insurer", on_delete=models.CASCADE, blank=True, null=True)
    customer = models.ForeignKey("sales.Customer", related_name="request_policy_customer", on_delete=models.CASCADE, blank=True, null=True)
    lead = models.ForeignKey("sales.Opportunity", related_name='request_by', on_delete=models.CASCADE,null=True, blank=True)
    request_by = models.ForeignKey("sales.User", related_name="request_policy_by", on_delete=models.CASCADE, blank=True, null=True)
    premium_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    quotation_document_size = models.BigIntegerField(blank=True, null=True)
    quotation_document = models.URLField(blank=True, null=True) 
    quotation_document_name = models.CharField(max_length=255, blank=True, null=True)
    request_type = models.ForeignKey(RequestType, on_delete=models.CASCADE)
    product = models.ForeignKey("sales.Product", related_name="request_policy_product", on_delete=models.CASCADE)
    payment_mode =  models.ForeignKey(PaymentPlan, related_name="request_policy_policy_plan", on_delete=models.CASCADE)
    coverage_type = models.ForeignKey(CoverageType, related_name="request_policy_coverage_type", on_delete=models.CASCADE)
    sum_insured = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    quotation_issued_date = models.DateField(blank=True, null=True)  
    quotation_expiry_date = models.DateField(blank=True, null=True) 
    policy_start_date = models.DateField() 
    policy_expiry_date = models.DateField() 
    quotation_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = "crmp_policy_base"

    def __str__(self):
        return f"Policy {self.policy_request_id} "






# from django.db import models
# from envoy_bu_crm_api.policy.models.crmp_request_type import RequestType, PaymentPlan
# from envoy_bu_crm_api.policy.models.crmp_coverage_type import CoverageType

# class RequestPolicy(models.Model):
#     policy_request_id = models.CharField(max_length=255,unique=True)
#     policy_request_date = models.DateField(auto_now_add=True)
#     risk_details_form = models.ForeignKey("sales.Form", related_name="request_policy_risk_details", on_delete=models.CASCADE, blank=True, null=True)
#     risk_type = models.ForeignKey("sales.OpportunityType", related_name="request_policy_risk_type", on_delete=models.CASCADE, blank=True, null=True)
#     insurer = models.ForeignKey("quotation.ServiceProvider", related_name="request_policy_insurer", on_delete=models.CASCADE, blank=True, null=True)
#     customer = models.ForeignKey("sales.Customer", related_name="request_policy_customer", on_delete=models.CASCADE, blank=True, null=True)
#     lead = models.ForeignKey("sales.Opportunity", related_name='request_by', on_delete=models.CASCADE,null=True, blank=True)
#     request_by = models.ForeignKey("sales.User", related_name="request_policy_by", on_delete=models.CASCADE, blank=True, null=True)
#     premium_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     entity = models.ForeignKey("sales.Entity", related_name='request_entity', on_delete=models.CASCADE,default=1)
#     status=models.ForeignKey("sales.Status",related_name="request_policy_status",on_delete=models.CASCADE,default=1)
#     quotation_document_size = models.BigIntegerField(blank=True, null=True)
#     quotation_document = models.URLField(blank=True, null=True) 
#     quotation_document_name = models.CharField(max_length=255, blank=True, null=True)
#     request_type = models.ForeignKey(RequestType, on_delete=models.CASCADE)
#     product = models.ForeignKey("sales.Product", related_name="request_policy_product", on_delete=models.CASCADE)
#     payment_mode =  models.ForeignKey(PaymentPlan, related_name="request_policy_policy_plan", on_delete=models.CASCADE)
#     coverage_type = models.ForeignKey(CoverageType, related_name="request_policy_coverage_type", on_delete=models.CASCADE)
#     sum_insured = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
#     quotation_issued_date = models.DateField(blank=True, null=True)  
#     quotation_expiry_date = models.DateField(blank=True, null=True) 
#     policy_start_date = models.DateField() 
#     policy_expiry_date = models.DateField() 
#     quotation_notes = models.TextField(blank=True, null=True)
#     class Meta:
#         db_table = "crmp_request_policies"

#     def __str__(self):
#         return f"Policy {self.policy_request_id} "







