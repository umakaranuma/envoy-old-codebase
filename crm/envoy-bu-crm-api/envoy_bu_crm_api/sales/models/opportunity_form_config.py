from django.db import models

from envoy_bu_crm_api.sales.models.core_models import Form

class OpportunityFormConfig(models.Model):
    ONBOARDING = "onboarding"
    QUOTATION_REQUEST = "quotation_request"
    CLAIM = "claim"
    CLAIM_EVALUATION = "claim_evaluation"
    CUSTOMER_POLICY = "customer_policy"
    CUSTOMER_QUOTATION = "customer_quotation"

    DATA_GATHERING_CHOICES = [
        (ONBOARDING, "Onboarding"),
        (QUOTATION_REQUEST, "Quotation Request"),
        (CLAIM, "Claim"),
        (CLAIM_EVALUATION, "Claim Evaluation"),
        (CUSTOMER_POLICY, "Customer Policy"),
        (CUSTOMER_QUOTATION, "Customer Quotation"),
    ]

    title = models.CharField(max_length=255)
    opportunity_type = models.ForeignKey("sales.OpportunityType", on_delete=models.CASCADE)
    data_gethering_type = models.CharField(max_length=255, choices=DATA_GATHERING_CHOICES)
    form = models.ForeignKey("sales.CoreTemplate", on_delete=models.RESTRICT,null=True, blank=True, related_name="opportunity_form_config")

    class Meta:
        db_table = "crm_opportunity_form_config"

    def __str__(self):
        return self.title