from django.db import models
from django.utils import timezone


class Incentive(models.Model):
    code = models.CharField(max_length=100, unique=True, db_index=True, null=True, blank=True)
    incentive_setup = models.ForeignKey(
        'IncentiveSetup', 
        on_delete=models.CASCADE, 
        db_column='incentive_setup_id',
        related_name='incentives',
        blank=True, null=True
    )
    agent = models.ForeignKey(
        'core_models.User', 
        on_delete=models.CASCADE, 
        db_column='agent_id',
        related_name='incentives',
        blank=True, null=True
    )
    performance_metric = models.ForeignKey(
        'PerformanceMetric', 
        on_delete=models.CASCADE, 
        db_column='performance_metric_id',
        related_name='incentives',
        blank=True, null=True
    )
    performance_metric_value = models.DecimalField(max_digits=10, decimal_places=2)
    actual_performance_value = models.DecimalField(max_digits=10, decimal_places=2)  # Actual commission amount
    reward_type = models.ForeignKey(
        'RewardType', 
        on_delete=models.CASCADE, 
        db_column='reward_type_id',
        related_name='incentives',
        blank=True, null=True
    )
    # Remove reward_type_value (now per-condition)
    # reward_type_value = models.DecimalField(max_digits=10, decimal_places=2)
    incentive_amount = models.DecimalField(max_digits=10, decimal_places=2)  # Calculated incentive amount
    commission_date = models.DateField()  # Date when commission was earned
    period_start = models.DateField(null=True, blank=True, help_text="Start date of the incentive period")
    period_end = models.DateField(null=True, blank=True, help_text="End date of the incentive period")
    repetition_type = models.CharField(max_length=50, null=True, blank=True)  # One-Time, Monthly, Quarterly
    status = models.CharField(max_length=20, default='pending')  # pending, approved, paid, cancelled
    notes = models.TextField(null=True, blank=True)
    # New: Store the matched condition (including reward_type_value) as JSON
    matched_condition = models.JSONField(null=True, blank=True, help_text="The matched condition from performance_fields, including reward_type_value.")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'crmf_incentives'
        verbose_name = 'Incentive'
        verbose_name_plural = 'Incentives'
        # CRITICAL: Database-level uniqueness constraint to prevent duplicate incentives
        # This ensures that the same setup + agent + period combination can only exist once
        # Even if Python logic fails, database will block duplicates
        # Note: We check deleted_at in queries, so this constraint applies to all records
        # If you need to allow duplicates for deleted records, you'll need a partial unique index via migration
        # Use field names (not db_column names) for unique_together
        unique_together = [['incentive_setup', 'agent', 'period_start', 'period_end']]

    def __str__(self):
        return f"Incentive {self.id} - Agent: {self.agent.display_name if self.agent else 'Unknown'} - Amount: {self.incentive_amount}"

