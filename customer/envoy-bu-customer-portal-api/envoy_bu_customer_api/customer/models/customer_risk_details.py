from django.db import models
from envoy_bu_customer_api.customer.models.customer_request import CustomerRequest

class CustomerRequestRiskDetails(models.Model):
    TYPE_CHOICES = [
        ("claim", "Claim"),
        ("policy", "Policy"),
        ("quotation", "Quotation"),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    customer_request = models.ForeignKey(
        CustomerRequest,
        on_delete=models.CASCADE,
        related_name="request_risk"
    )
    document_name = models.CharField(max_length=255, null=True, blank=True)
    document_link = models.CharField(max_length=2048, null=True, blank=True)  # changed to CharField
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cus_request_risk_details"
        # unique_together = ("customer_request", "document_link")

    def __str__(self):
        return f"Request #{self.customer_request.id} - Link {self.document_link}"
