from django.db import models
from envoy_bu_customer_api.customer.models.customer_request import CustomerRequest
from core_models.core_models import ProductDocumentType

class CustomerRequestDocument(models.Model):
    TYPE_CHOICES = [
        ("claim", "Claim"),
        ("policy", "Policy"),
        ("quotation", "Quotation"),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES,default="claim")
    customer_request = models.ForeignKey(
        CustomerRequest,
        on_delete=models.CASCADE,
        related_name="documents"
    )
    document_type = models.ForeignKey(
        ProductDocumentType,
        on_delete=models.CASCADE,
        related_name="request_documents"
    )
    value = models.TextField(null=True, blank=True)  
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # is_draft = models.BooleanField(default=True)

    class Meta:
        db_table = "cus_request_document_submissions"
        unique_together = ("customer_request", "document_type")

    def __str__(self):
        return f"Request #{self.customer_request.id} - DocType #{self.document_type.id}"
