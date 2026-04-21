from django.db import models
from envoy_bu_crm_api.policy.models.crmp_issued_policies import IssuedPolicy

class Notes(models.Model):
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    health = models.CharField(max_length=255, blank=True, null=True)
    entity = models.ForeignKey("sales.Entity", related_name="policy_notes", on_delete=models.CASCADE, default=1)
    issued_policy = models.ForeignKey(IssuedPolicy, related_name="policy_notes", on_delete=models.CASCADE, default=1)

    class Meta:
        db_table = "crmp_notes"

    def __str__(self):
        return f"Note {self.id} - {self.title}"
