from django.db import models
from .report_type import ReportType


class Report(models.Model):
    title = models.CharField(max_length=200)
    type_id = models.ForeignKey(ReportType, on_delete=models.CASCADE, related_name='reports')
    entity_id = models.BigIntegerField(unique=True)
    views = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    query = models.TextField(null=True, blank=True)
    json = models.JSONField(null=True, blank=True)
    created_by_id = models.BigIntegerField()
    updated_by_id = models.BigIntegerField(null=True, blank=True)
    deleted_by_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'rep_reports'
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'

    def __str__(self):
        return self.title 