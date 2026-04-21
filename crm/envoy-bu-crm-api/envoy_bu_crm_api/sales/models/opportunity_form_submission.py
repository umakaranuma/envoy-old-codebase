from django.db import models

from envoy_bu_crm_api.sales.models.core_models import CoreFormSubmission



class OpportunityFormSubmission(models.Model):
    opportunity = models.ForeignKey("sales.Opportunity", on_delete=models.CASCADE,null=True, blank=True)
    form_submission = models.ForeignKey(CoreFormSubmission, on_delete=models.RESTRICT)
    oppor_form_config = models.ForeignKey("sales.OpportunityFormConfig", on_delete=models.RESTRICT)
    customer = models.ForeignKey("sales.Customer", on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "crm_oppor_form_submissions"