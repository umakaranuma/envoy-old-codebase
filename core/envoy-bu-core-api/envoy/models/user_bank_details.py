from django.db import models

from envoy.models.user import User
from .service_provider import ServiceProvider

class CoreUserBankDetail(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sp', blank=True, null=True)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.CASCADE, related_name='bank_details', blank=True, null=True)
    account_holder_name = models.CharField(max_length=255)
    bank_name = models.CharField(max_length=100)
    bank_branch = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    iban_swift_code = models.CharField(max_length=50, blank=True, null=True)
    payment_gateway_url =models.CharField(max_length=100,blank=True,null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_user_bank_details"

    def __str__(self):
        return f"{self.account_holder_name} - {self.bank_name}"
