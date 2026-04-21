from django.db import models


class ReportType(models.Model):
    entity_id = models.BigIntegerField(unique=True)
    name = models.CharField(max_length=100)
    module = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    created_by_id = models.BigIntegerField()
    updated_by_id = models.BigIntegerField(null=True, blank=True)
    deleted_by_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'rep_report_types'
        verbose_name = 'Report Type'
        verbose_name_plural = 'Report Types'

    def __str__(self):
        return self.name 