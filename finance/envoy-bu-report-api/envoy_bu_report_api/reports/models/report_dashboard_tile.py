from django.db import models
from .report_dashboard import ReportDashboard
from .report_chart import ReportChart
from .report import Report


class ReportDashboardTile(models.Model):
    entity_id = models.BigIntegerField(unique=True)
    dashboard_id = models.ForeignKey(ReportDashboard, on_delete=models.CASCADE, related_name='tiles')
    chart_id = models.ForeignKey(ReportChart, on_delete=models.CASCADE, null=True, blank=True, related_name='dashboard_tiles')
    report_id = models.ForeignKey(Report, on_delete=models.CASCADE, related_name='dashboard_tiles')
    type = models.CharField(max_length=50)
    created_by_id = models.BigIntegerField()
    updated_by_id = models.BigIntegerField(null=True, blank=True)
    deleted_by_id = models.BigIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'rep_report_dashboard_tiles'
        verbose_name = 'Report Dashboard Tile'
        verbose_name_plural = 'Report Dashboard Tiles'

    def __str__(self):
        return f"Tile {self.entity_id} - {self.type}" 