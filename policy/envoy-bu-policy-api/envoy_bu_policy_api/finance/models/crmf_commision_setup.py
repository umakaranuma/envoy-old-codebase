from django.db import models
from .crmf_transaction_types import TransactionType
from core_models.core_models import ProductGroup

class CommissionSetupTeam(models.Model):
    """
    Many-to-many relationship between CommissionSetup and Teams.
    """
    id = models.AutoField(primary_key=True)
    commission_setup = models.ForeignKey('CommissionSetup', on_delete=models.CASCADE, db_column='commission_setup_id')
    team_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'crmf_commission_setup_teams'
        verbose_name = 'Commission Setup Team'
        verbose_name_plural = 'Commission Setup Teams'
        unique_together = ('commission_setup', 'team_id')

    def __str__(self):
        return f"Commission Setup {self.commission_setup_id} - Team {self.team_id}"

class CommissionSetup(models.Model):
    """
    Represents the commission setup for CRMF.
    """
    id = models.AutoField(primary_key=True)
    product_id = models.IntegerField(null=True, blank=True)
    native_product_id = models.IntegerField(null=True, blank=True)
    insurer_id = models.IntegerField(null=True, blank=True)
    transaction_type = models.ForeignKey(TransactionType, on_delete=models.PROTECT, db_column='transaction_type', null=True)
    # Remove single team field and add many-to-many relationship
    # sales_team_id = models.IntegerField()
    brokerage_revenue_percent = models.DecimalField(max_digits=20, decimal_places=2)
    agent_commission_percent = models.DecimalField(max_digits=20, decimal_places=2)
    entity_id = models.BigIntegerField(null=True, blank=True)
    product_group = models.ForeignKey(ProductGroup, on_delete=models.PROTECT, db_column='product_group_id', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'crmf_commission_setups'
        verbose_name = 'Commission Setup'
        verbose_name_plural = 'Commission Setups'

    def __str__(self):
        return f"{self.transaction_type.name} - {self.brokerage_revenue_percent}%"

    def get_team_ids(self):
        """Get list of team IDs associated with this commission setup."""
        return list(CommissionSetupTeam.objects.filter(
            commission_setup=self
        ).values_list('team_id', flat=True))

    def set_team_ids(self, team_ids):
        """Set team IDs for this commission setup."""
        # Remove existing team associations
        CommissionSetupTeam.objects.filter(commission_setup=self).delete()
        # Add new team associations
        for team_id in team_ids:
            CommissionSetupTeam.objects.create(
                commission_setup=self,
                team_id=team_id
            )