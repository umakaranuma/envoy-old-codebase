from django.db import models
from core_models.core_models import User

class CrmfAgentSalesTarget(models.Model):
    PERIOD_TYPE_CHOICES = [
        ("monthly", "Monthly"),
        ("yearly", "Yearly"),
    ]

    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name="agent_sales_targets")
    period_type = models.CharField(max_length=10, choices=PERIOD_TYPE_CHOICES)
    month = models.IntegerField(null=True, blank=True, help_text="1-12 for monthly targets")
    year = models.IntegerField(null=True, blank=True)
    target_amount = models.DecimalField(max_digits=15, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "crmf_agent_sales_targets"
        verbose_name = "Agent Sales Target"
        verbose_name_plural = "Agent Sales Targets"
        unique_together = ("agent", "period_type", "month", "year","deleted_at")

    def __str__(self):
        return f"Agent {self.agent_id} - {self.period_type} {self.month or ''}/{self.year} - {self.target_amount}" 