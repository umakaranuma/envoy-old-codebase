from django.db import models
from envoy_bu_customer_api.customer.models.customer_request import CustomerRequest


class CustomerRequestCoverageDetails(models.Model):
    TYPE_CHOICES = [
        ("claim", "Claim"),
        ("policy", "Policy"),
        ("quotation", "Quotation"),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES,default="claim")
    customer_request = models.OneToOneField(
        CustomerRequest,
        on_delete=models.CASCADE,
        related_name="coverage_details"
    )
    sum_insured = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    # is_draft = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cus_coverage_request_details"

    def __str__(self):
        return f"Request #{self.customer_request.id} - Coverage Details"
