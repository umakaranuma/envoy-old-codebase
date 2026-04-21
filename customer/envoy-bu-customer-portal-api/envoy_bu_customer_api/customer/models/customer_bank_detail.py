# from django.db import models

# class CustomerBankDetail(models.Model):
#     id = models.BigAutoField(primary_key=True, unique=True,)
#     customer_id = models.BigIntegerField(blank=True, null=True)
#     doc = models.CharField(max_length=255, blank=True, null=True)
#     doc_type = models.CharField(max_length=100, blank=True, null=True)
#     doc_name = models.CharField(max_length=255, blank=True, null=True)
#     account_holder_name = models.CharField(max_length=255)
#     bank_name = models.CharField(max_length=255)
#     bank_branch = models.CharField(max_length=255)
#     account_number = models.CharField(max_length=64)
#     iban_swift_code = models.CharField(max_length=64, blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     deleted_at = models.DateTimeField(blank=True, null=True)

#     class Meta:
#         db_table = "cus_bank_details"
     

#     def __str__(self):
#         return f"{self.account_holder_name} - {self.bank_name} ({self.account_number})" 