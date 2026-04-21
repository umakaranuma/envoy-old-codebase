from django.conf import settings
from django.db import models


class ClaimStatusHistory(models.Model):
    claim = models.ForeignKey("claims.Claim", on_delete=models.CASCADE, related_name="status_history")
    from_status = models.ForeignKey(
        "core_models.Status",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="claim_status_from_history",
    )
    to_status = models.ForeignKey(
        "core_models.Status",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="claim_status_to_history",
    )
    changed_by = models.ForeignKey(
        "core_models.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="claim_status_changes",
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "crmp_claim_status_history"
        ordering = ["-changed_at"]

    def __str__(self):
        from_status = self.from_status.name if self.from_status else "None"
        to_status = self.to_status.name if self.to_status else "None"
        return f"Claim {self.claim_id}: {from_status} -> {to_status}"

