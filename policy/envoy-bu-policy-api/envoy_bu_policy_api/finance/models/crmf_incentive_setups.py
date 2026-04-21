from django.db import models
from django.utils import timezone


class IncentiveSetup(models.Model):
    name = models.CharField(max_length=255)
    incentive_code = models.CharField(max_length=100, unique=True, db_index=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    repeation_type = models.CharField(max_length=50)  # One-Time, Monthly, Quarterly
    start_date = models.DateField()
    end_date = models.DateField()
    # Reward type (fixed, percentage, etc.)
    reward_type = models.ForeignKey(
        'RewardType',
        on_delete=models.CASCADE,
        db_column='reward_type_id',
        related_name='incentive_setups',
        null=True, blank=True
    )
    reward_type_value = models.FloatField(default=0)  # Value for reward type (e.g., amount, percent)
    performance_fields = models.JSONField(null=True, blank=True)  # Store selected fields/conditions as JSON
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    incentive_base_field = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        db_table = 'crmf_incentive_setups'
        verbose_name = 'Incentive Setup'
        verbose_name_plural = 'Incentive Setups'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name}"


class PerformanceMetric(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    metric_type = models.CharField(max_length=50, default='commission')  # commission, sales, etc.
    unit = models.CharField(max_length=20, default='amount')  # amount, percentage, count, etc.
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'crmf_performance_metrics'
        verbose_name = 'Performance Metric'
        verbose_name_plural = 'Performance Metrics'

    def __str__(self):
        return self.name


class RewardType(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    reward_type = models.CharField(max_length=50, default='fixed')  # fixed, percentage, tiered
    calculation_method = models.CharField(max_length=100, null=True, blank=True)  # How to calculate the reward
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'crmf_reward_types'
        verbose_name = 'Reward Type'
        verbose_name_plural = 'Reward Types'

    def __str__(self):
        return self.name


