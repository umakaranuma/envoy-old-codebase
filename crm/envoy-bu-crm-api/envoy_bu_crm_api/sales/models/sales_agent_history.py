from django.db import models
from django.utils import timezone

from envoy_bu_crm_api.sales.models.core_models import User
from envoy_bu_crm_api.sales.models.opportunities import Opportunity


class SalesAgentHistory(models.Model):
    """
    Model to track sales agent changes for opportunities only
    Task assignee changes are tracked in core_task_assignee_histories table
    """
    LEAD = "lead"
    
    TYPE_CHOICES = [
        (LEAD, "Lead"),
    ]
    
    # Change details
    from_agent = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="sales_agent_from_changes",
        help_text="Previous sales agent"
    )
    to_agent = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="sales_agent_to_changes",
        help_text="New sales agent"
    )
    changed_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="sales_agent_changes_made",
        help_text="User who made the change"
    )
    updated_at = models.DateTimeField(default=timezone.now)
    
    # Reference fields
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, help_text="Type of change: lead only")
    lead = models.ForeignKey(
        Opportunity, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        help_text="Opportunity ID (for lead changes)"
    )
    
    class Meta:
        db_table = "crm_sales_agent_histories"
        ordering = ["-updated_at"]
        verbose_name = "Sales Agent History"
        verbose_name_plural = "Sales Agent Histories"
    
    def __str__(self):
        from_name = self.from_agent.display_name if self.from_agent else "None"
        to_name = self.to_agent.display_name if self.to_agent else "None"
        return f"{self.type.title()} - {from_name} → {to_name}"

