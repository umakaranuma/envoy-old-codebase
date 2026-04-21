from django.db import models

from core_models.core_models import CoreFormSubmission, Customer, OpportunityType, ProductGroup, Status, VendorProducts

class CustomerRequest(models.Model):
    TYPE_CHOICES = [
        ("claim", "Claim"),
        ("policy", "Policy"),
        ("quotation", "Quotation"),
    ]

    form_submission = models.ForeignKey(CoreFormSubmission, on_delete=models.CASCADE,null=True, blank=True)
    code = models.CharField(max_length=20, unique=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    submitted_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)
    is_draft = models.BooleanField(default=True)


    class Meta:
        db_table = "cus_requests"


class CustomerRequestRiskType(models.Model):
    customer_request = models.ForeignKey(CustomerRequest, on_delete=models.CASCADE, related_name="risk_types")
    risk_type = models.ForeignKey(OpportunityType, on_delete=models.CASCADE)

    class Meta:
        db_table = "cus_request_risk_types"


class CustomerRequestVendorProduct(models.Model):
    customer_request = models.ForeignKey(CustomerRequest, on_delete=models.CASCADE, related_name="vendor_products")
    vendor_product = models.ForeignKey(VendorProducts, on_delete=models.CASCADE, null=True, blank=True)
    product_group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        db_table = "cus_request_vendor_products"
