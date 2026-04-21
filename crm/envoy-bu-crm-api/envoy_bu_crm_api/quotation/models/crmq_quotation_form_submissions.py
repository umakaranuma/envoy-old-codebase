from django.db import models

class QuotationFormSubmission(models.Model):
    id = models.AutoField(primary_key=True)
    vendor_quotation_id = models.BigIntegerField(blank=True, null=True)
    form_submission_id = models.BigIntegerField(blank=True, null=True)
    by_user_id = models.BigIntegerField(blank=True, null=True)
    class Meta:
        db_table = 'crmq_quotation_form_submissions'
        verbose_name = 'QuotationFormSubmission'
        verbose_name_plural = 'QuotationFormSubmissions'

    def __str__(self):
        return self.id 