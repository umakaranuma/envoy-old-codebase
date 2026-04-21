from django.db import models

class VendorQuotationResponse(models.Model):
    quotation = models.ForeignKey("quotation.Quotation", on_delete=models.CASCADE)
    service_provider = models.ForeignKey("sales.ServiceProvider", on_delete=models.CASCADE)
    by_user = models.ForeignKey("sales.User", on_delete=models.CASCADE)
    vendor_quotation = models.ForeignKey("quotation.QuotationServiceProvider", on_delete=models.CASCADE)

    code = models.CharField(max_length=100, unique=True)
    coverage_details = models.TextField()
    coverage_details_type = models.CharField(max_length=100)
    coverage_details_name = models.CharField(max_length=100)
    received_date = models.DateField()
    expiry_date = models.DateField()
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=100)
    re_request = models.BooleanField(default=False)
    version = models.CharField(max_length=20, default="1.0")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "crmq_vendor_response"
