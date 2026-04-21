from django.db import models
from envoy_bu_customer_api.customer.models.customer_request import CustomerRequest

class PolicyHolder(models.Model):
    TYPE_CHOICES = [
        ("claim", "Claim"),
        ("policy", "Policy"),
        ("quotation", "Quotation"),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES,default="claim")
    customer_request = models.OneToOneField(
        CustomerRequest,
        on_delete=models.CASCADE,
        related_name="policy_holder"
    )
    policy_holder_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=50)
    nic = models.CharField(max_length=25)
    phone_number = models.CharField(max_length=20)
    email = models.EmailField()
    address = models.TextField()
    contact_method = models.CharField(max_length=50)
    # is_draft = models.BooleanField(default=True)

    class Meta:
        db_table = "cus_policy_holders"

    def __str__(self):
        return f"{self.policy_holder_name} ({self.customer_request.code})"
