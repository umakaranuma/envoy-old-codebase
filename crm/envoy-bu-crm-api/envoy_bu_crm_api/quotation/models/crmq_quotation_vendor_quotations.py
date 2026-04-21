

from django.db import models

class QuotationVendorQuotation(models.Model):
    id = models.AutoField(primary_key=True)
    send_quotation_id = models.BigIntegerField(blank=True, null=True)
    vendor_quotation_id = models.BigIntegerField(blank=True, null=True)
    
    class Meta:
        db_table = 'crmq_quotation_vendor_quotations'
        verbose_name = 'QuotationVendorQuotation'
        verbose_name_plural = 'QuotationVendorQuotations'

    def __str__(self):
        return self.id 

