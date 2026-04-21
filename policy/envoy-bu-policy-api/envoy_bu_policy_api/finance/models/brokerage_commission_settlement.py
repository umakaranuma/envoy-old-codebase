from django.db import models
from core_models.core_models import Entity
from .crmf_brokerage_commission import BrokerageCommission
from .crmf_agent_commission import AgentCommission


class BrokerageCommissionSettlement(models.Model):
    """
    Unified commission settlement table.
    Stores settlement history for both brokerage and agent commissions.
    """

    COMMISSION_TYPE_CHOICES = [
        ("BROKERAGE_COMMISSION", "Brokerage Commission"),
        ("AGENT_COMMISSION", "Agent Commission"),
    ]

    commission_type = models.CharField(
        max_length=32,
        choices=COMMISSION_TYPE_CHOICES,
        default="BROKERAGE_COMMISSION",
        db_index=True,
    )

    brokerage_commission = models.ForeignKey(
        BrokerageCommission,
        on_delete=models.CASCADE,
        related_name="settlements",
        null=True,
        blank=True,
    )
    agent_commission = models.ForeignKey(
        AgentCommission,
        on_delete=models.CASCADE,
        related_name="settlements",
        null=True,
        blank=True,
    )
    settlement_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    settlement_type = models.CharField(
        max_length=30,
        choices=[
            ('settlement', 'Settlement'),
            ('physical_credit_note', 'Physical Credit Note'),
        ],
        default='settlement'
    )
    settlement_date = models.DateTimeField(auto_now_add=True)
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="brokerage_commission_settlements"
    )

    class Meta:
        db_table = "crmf_brokerage_commission_settlements"
        verbose_name = "Brokerage / Agent Commission Settlement"
        verbose_name_plural = "Brokerage / Agent Commission Settlements"
        ordering = ['-settlement_date', '-entity__created_at']

    def __str__(self):
        if self.brokerage_commission_id:
            target = f"Brokerage Commission {self.brokerage_commission_id}"
        elif self.agent_commission_id:
            target = f"Agent Commission {self.agent_commission_id}"
        else:
            target = "Commission"
        return f"Settlement for {target} - {self.settlement_amount}"

    @classmethod
    def get_commission_outstanding_amount(cls, commission_id):
        """Calculate outstanding amount for a specific brokerage commission"""
        commission = BrokerageCommission.objects.get(id=commission_id)
        # Outstanding = recognized - realized - deductible (if negative, return 0)
        commission_deductible = getattr(commission, 'commission_deductible', 0) or 0
        return max(0, commission.revenue_recognized - commission.revenue_realized - commission_deductible)

    @classmethod
    def get_commission_settlement_summary(cls, commission_id):
        """Get detailed settlement summary for a brokerage commission"""
        commission = BrokerageCommission.objects.get(id=commission_id)
        # Get settlement history for this commission
        settlements = cls.objects.filter(brokerage_commission_id=commission_id)
        total_settled = settlements.aggregate(
            total=models.Sum('settlement_amount')
        )['total'] or 0
        # Outstanding = recognized - realized - deductible (if negative, return 0)
        commission_deductible = getattr(commission, 'commission_deductible', 0) or 0
        outstanding = max(0, commission.revenue_recognized - commission.revenue_realized - commission_deductible)
        return {
            'commission_id': commission_id,
            'revenue_recognized': commission.revenue_recognized,
            'revenue_realized': commission.revenue_realized,
            'commission_deductible': commission_deductible,
            'total_settled': total_settled,
            'outstanding': outstanding,
            'settlement_count': settlements.count()
        }


