from django.db import models

from envoy_bu_crm_api.sales.models.core_models import FormSubmission

class PolicyFormSubmission(models.Model):
    policy = models.ForeignKey("policy.IssuedPolicy", on_delete=models.CASCADE,blank=True, null=True)
    policy_request = models.ForeignKey("policy.RequestPolicy", on_delete=models.CASCADE,blank=True, null=True)
    form_submission = models.ForeignKey(FormSubmission, on_delete=models.RESTRICT)
    oppor_form_config = models.ForeignKey("sales.OpportunityFormConfig", on_delete=models.RESTRICT)

    class Meta:
      db_table = "crmp_policy_risk_reg_form_submissions"