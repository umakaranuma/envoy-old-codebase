from django.db import models

class QuotationAttribute(models.Model):
    id = models.AutoField(primary_key=True)
    quotation_id = models.BigIntegerField(blank=True, null=True)
    form_submission_id = models.BigIntegerField(blank=True, null=True)
    attribute_id = models.BigIntegerField(blank=True, null=True)
    class Meta:
        db_table = 'crmq_quotation_attributes'
        verbose_name = 'QuotationAttribute'
        verbose_name_plural = 'QuotationAttributes'

    def __str__(self):
        return self.id 

