from django.db import models
from envoy_bu_policy_api.policy.models.crmp_issued_policies import IssuedPolicy


class PolicyInheritance(models.Model):
    start_date = models.DateTimeField()
    policy_effective_date = models.DateField(blank=True, null=True)
    issued_policy = models.ForeignKey(
        IssuedPolicy,
        related_name="renwal_policy",
        on_delete=models.CASCADE,
        default=1,
    )
    entity = models.ForeignKey(
        "core_models.Entity",
        related_name="renewal_policy_entity",
        on_delete=models.CASCADE,
        default=1,
    )

    class Meta:
        db_table = "crmp_issued_policies_inheritance"

    def __str__(self):
        return f"Policy {self.brokerage_policy_id}"
