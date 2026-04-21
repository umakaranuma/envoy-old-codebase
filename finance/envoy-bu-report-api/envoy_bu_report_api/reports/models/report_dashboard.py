from django.db import models


class ReportDashboard(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=255, null=True, blank=True)
    entity_id = models.BigIntegerField(unique=True)
    module = models.CharField(max_length=100)
    created_by_id = models.BigIntegerField()
    updated_by_id = models.BigIntegerField(null=True, blank=True)
    deleted_by_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'rep_report_dashboards'
        verbose_name = 'Report Dashboard'
        verbose_name_plural = 'Report Dashboards'

    def __str__(self):
        return self.title 