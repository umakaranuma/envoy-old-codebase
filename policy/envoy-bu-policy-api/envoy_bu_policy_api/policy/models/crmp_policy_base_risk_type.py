from django.db import models

from envoy_bu_policy_api.policy.models.crmp_policy_base import PolicyBase


class PolicyBaseRiskType(models.Model):
    policy_base = models.ForeignKey(PolicyBase, on_delete=models.CASCADE, related_name="risk_types")
    risk_type = models.ForeignKey("core_models.OpportunityType", on_delete=models.CASCADE)

    class Meta:
        db_table = "crmp_policy_base_risk_types"
