from django.db import models


class UserCommission(models.Model):
    """
    Represents user-specific commission settings.
    """
    id = models.AutoField(primary_key=True)
    team_id = models.IntegerField(null=True ,blank=True)
    user_id = models.IntegerField()
    commission_percent = models.DecimalField(max_digits=5, decimal_places=2)
    revised_commission_percent = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    commission_setup_id = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'crmf_user_commissions'
        verbose_name = 'User Commission'
        verbose_name_plural = 'User Commissions'

    def __str__(self):
        return self
