from django.db import models
from .report import Report


class ReportChart(models.Model):
    report_id = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='charts')
    title = models.CharField(max_length=100)
    type = models.CharField(max_length=50)
    json = models.JSONField()
    description = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'rep_report_charts'
        verbose_name = 'Report Chart'
        verbose_name_plural = 'Report Charts'

    def __str__(self):
        return self.title 