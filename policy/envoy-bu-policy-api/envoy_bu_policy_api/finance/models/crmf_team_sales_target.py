from django.db import models
from core_models.core_models import Team

class CrmfTeamSalesTarget(models.Model):
    PERIOD_TYPE_CHOICES = [
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, db_column='team_id', related_name='sales_targets', help_text="Reference to core_teams table")
    period_type = models.CharField(max_length=10, choices=PERIOD_TYPE_CHOICES)
    month = models.IntegerField(null=True, blank=True, help_text="1-12 for monthly targets")
    year = models.IntegerField(null=True, blank=True)
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "crmf_team_sales_targets"
        verbose_name = "Team Sales Target"
        verbose_name_plural = "Team Sales Targets"
        unique_together = ("team", "period_type", "month", "year","deleted_at")

    def __str__(self):
        return f"Team {self.team_id} - {self.period_type} {self.month or ''}/{self.year} - {self.target_amount}" 