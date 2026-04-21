from django.db import models

from core_models.core_models import ProductDocumentType
from envoy_bu_policy_api.policy.models.crmp_policy_base import PolicyBase

class PolicyRequestDocument(models.Model): 
   
   
    policy_base= models.ForeignKey( 
        PolicyBase, 
        on_delete=models.CASCADE,
        related_name="policy_documents"
    )
    document_type = models.ForeignKey(
        ProductDocumentType,
        on_delete=models.CASCADE,
        related_name="request_documents"
    )
    value = models.TextField(null=True, blank=True)  
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "crmp_policy_documents" 
        unique_together = ("policy_base", "document_type")

    def __str__(self):
        return f"Request #{self.policy_base.id} - DocType #{self.document_type.id}"
