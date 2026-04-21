from django.db import models
from envoy_bu_crm_api.policy.models.crmp_issued_policies import IssuedPolicy
from .crmp_request_policies import RequestPolicy 

class Document(models.Model):
    CATEGORY_POLICY = "Policy-Related"
    CATEGORY_RISK   = "Risk-Related"
    CATEGORY_CHOICES = [
        (CATEGORY_POLICY, "Policy-Related"),
        (CATEGORY_RISK,   "Risk-Related"),
    ]

    document_category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default=CATEGORY_POLICY,
    )
    entity = models.ForeignKey("sales.Entity", related_name="policy_documents", on_delete=models.CASCADE, default=1)
    issued_policy = models.ForeignKey(IssuedPolicy, related_name="policy_documents", on_delete=models.CASCADE, blank=True, null=True)
    request_policy = models.ForeignKey(RequestPolicy, related_name="policy_documents_req", on_delete=models.CASCADE, blank=True, null=True)
    
    class Meta:
        db_table = "crmp_documents"

    def __str__(self):
        return f"Document {self.id} - {self.file_name}"
