from django.db import models
from envoy_bu_policy_api.claims.models.claim import Claim
from core_models.crm_models import RiskSubmission


class ClaimRisk(models.Model):
    """
    Model to store the relationship between claims and risk submissions.
    This allows a claim to be associated with multiple risk submissions.
    """
    claim = models.ForeignKey(
        Claim,
        related_name='claim_risks',
        on_delete=models.CASCADE,
        help_text="The claim this risk submission is associated with"
    )
    risk_submission = models.ForeignKey(
        RiskSubmission,
        related_name='claim_risks',
        on_delete=models.CASCADE,
        help_text="The risk submission associated with this claim"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "crmp_claim_risks"
        unique_together = ['claim', 'risk_submission']
        indexes = [
            models.Index(fields=['claim']),
            models.Index(fields=['risk_submission']),
        ]

    def __str__(self):
        return f"Claim {self.claim.id} - Risk Submission {self.risk_submission.id}"
