from django.db import models

from envoy.models.service_provider import ServiceProvider

class ServiceProviderBankDetail(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name="bank_details")

    account_holder_name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=255)
    bank_branch = models.CharField(max_length=255)
    account_number = models.CharField(max_length=50)
    iban_swift_code = models.CharField(max_length=100, blank=True, null=True)
    payment_gateway_url = models.URLField(blank=True, null=True)

    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_service_provider_details"

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"
