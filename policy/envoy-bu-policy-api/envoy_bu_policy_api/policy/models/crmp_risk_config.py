from django.db import models

from core_models.crm_models import Risk, RiskSubmission
from envoy_bu_policy_api.policy.models.crmp_policy_base import PolicyBase
from envoy_bu_policy_api.policy.models.crmp_request_policies import RequestPolicy

class PolicyRiskConfig(models.Model):
    risk_submission = models.ForeignKey(RiskSubmission, on_delete=models.CASCADE)
    policy_base = models.ForeignKey(PolicyBase, on_delete=models.CASCADE)

    class Meta:
        db_table = 'crmp_policy_risk_config'
        unique_together = ['policy_base', 'risk_submission']  # Prevent duplicate policy-submission combinations

    def __str__(self):
        return f"Policy Base: {self.policy_base.id} - Risk Submission ID: {self.risk_submission.id}"
