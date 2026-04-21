# models.py
import uuid
from django.db import models
from .crmp_endorsement_request import EndorsementRequest
from envoy_bu_policy_api.service import EndorsementStatus

class Endorsement(models.Model):
    endorsement_request = models.ForeignKey(
        EndorsementRequest, related_name="endorsement_details", on_delete=models.CASCADE,default=1
    )
    endorsement_id = models.CharField(max_length=255, unique=True, editable=False)
    endorsement_date = models.DateField(auto_now_add=True)
    status = models.IntegerField(choices=EndorsementStatus.choices,default=1)
    remarks = models.TextField(blank=True, null=True)
    credit_period_days = models.IntegerField(blank=True, null=True)
    credit_age_days = models.IntegerField(blank=True, null=True)
    insurer_invoice_id = models.CharField(max_length=255, blank=True, null=True)  # Insurer Invoice ID

    def save(self, *args, **kwargs):
        if not self.endorsement_id:
            # Format: END20250412-uuid4short
            self.endorsement_id = f"END{self.endorsement_date.strftime('%Y%m%d') if self.endorsement_date else ''}-{uuid.uuid4().hex[:6].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Endorsement {self.endorsement_id}"

    class Meta:
        db_table = "crmp_endorsements_details"
