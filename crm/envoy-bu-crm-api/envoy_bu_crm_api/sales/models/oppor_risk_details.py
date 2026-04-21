from django.db import models
from django.utils import timezone

from envoy_bu_crm_api.sales.models.OpportunityType import OpportunityType
from envoy_bu_crm_api.sales.models.core_models import CoreFormSubmission, Customer, Status
from envoy_bu_crm_api.sales.models.opportunities import Opportunity

class RiskDetail(models.Model):
    code = models.CharField(max_length=20, unique=True, editable=False)
    lead = models.ForeignKey(Opportunity, on_delete=models.CASCADE, null=True, blank=True)
    risk_type = models.ForeignKey(OpportunityType, on_delete=models.SET_NULL, null=True,blank=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    submission = models.ForeignKey(CoreFormSubmission, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    recommendation_document = models.FileField( null=True, blank=True)

    class Meta:
        db_table = 'crm_risk_details'

    def __str__(self):
        return self.code
