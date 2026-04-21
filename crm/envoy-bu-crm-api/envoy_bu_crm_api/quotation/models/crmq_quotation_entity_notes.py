from django.db import models

class QuotationEntityNote(models.Model):
    id = models.AutoField(primary_key=True)
    quotation_id = models.BigIntegerField(blank=True, null=True)
    entity_id = models.BigIntegerField(blank=True, null=True)
    form_submission_id = models.BigIntegerField(blank=True, null=True)
    class Meta:
        db_table = 'crmq_quotation_entity_notes'
        verbose_name = 'QuotationEntityNote'
        verbose_name_plural = 'QuotationEntityNotes'

    def __str__(self):
        return self.id 