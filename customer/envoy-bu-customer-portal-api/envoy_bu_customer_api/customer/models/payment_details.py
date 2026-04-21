from django.db import models
from envoy_bu_customer_api.customer.models.customer_request import CustomerRequest

class CustomerRequestPaymentDetails(models.Model):
    TYPE_CHOICES = [
        ("claim", "Claim"),
        ("policy", "Policy"),
        ("quotation", "Quotation"),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES,default="claim")
    customer_request = models.OneToOneField(
        CustomerRequest,
        on_delete=models.CASCADE,
        related_name="payment_details"
    )
    payment_method = models.CharField(max_length=100, default="Unknown")
    payment_frequency = models.CharField(max_length=100, default="Monthly")
    bank_number = models.CharField(max_length=50, default="000000")
    account_holder_name = models.CharField(max_length=255, default="Unknown")
    branch = models.CharField(max_length=100, default="Main Branch")
    bank_name = models.CharField(max_length=255, default="Default Bank")
    iban_swift_code = models.CharField(max_length=100, null=True, blank=True)  # Still nullable
    estimated_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    # is_draft = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "cus_payment_request_details"

    def __str__(self):
        return f"Payment Details for Request #{self.customer_request.id}"
