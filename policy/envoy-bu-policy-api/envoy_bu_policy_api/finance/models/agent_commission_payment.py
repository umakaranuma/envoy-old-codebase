from django.db import models
from core_models.core_models import Entity
from .crmf_agent_commission import AgentCommission

class AgentCommissionPayment(models.Model):
    agent_commission = models.ForeignKey(
        AgentCommission,
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True
    )
    incentive = models.ForeignKey(
        'Incentive',
        on_delete=models.CASCADE,
        related_name="payments",
        null=True,
        blank=True
    )
    payment_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_type = models.CharField(
        max_length=20,
        choices=[
            ('commission', 'Commission'),
            ('incentive', 'Incentive')
        ],
        default='commission'
    )
    payment_date = models.DateTimeField(auto_now_add=True)
    entity = models.ForeignKey(
        Entity,
        on_delete=models.CASCADE,
        related_name="agent_commission_payments"
    )

    class Meta:
        db_table = "crmf_agent_commission_payments"
        verbose_name = "Agent Commission Payment"
        verbose_name_plural = "Agent Commission Payments"
        ordering = ['-payment_date', '-entity__created_at']

    def __str__(self):
        payment_for = f"Commission {self.agent_commission.id}" if self.agent_commission else f"Incentive {self.incentive.id}"
        return f"Payment for {payment_for} - {self.payment_amount}"

    def save(self, *args, **kwargs):
        # Set payment type based on which field is populated
        if self.agent_commission and not self.incentive:
            self.payment_type = 'commission'
        elif self.incentive and not self.agent_commission:
            self.payment_type = 'incentive'
        
        super().save(*args, **kwargs)

    @classmethod
    def get_commission_outstanding_amount(cls, commission_id):
        """Calculate outstanding amount for a specific commission"""
        commission = AgentCommission.objects.get(id=commission_id)
        # Outstanding = recognized - realized - deductible (if negative, return 0)
        commission_deductible = getattr(commission, 'commission_deductible', 0) or 0
        return max(0, commission.revenue_recognized - commission.revenue_realized - commission_deductible)

    @classmethod
    def get_commission_payment_summary(cls, commission_id):
        """Get detailed payment summary for a commission"""
        commission = AgentCommission.objects.get(id=commission_id)
        # Get payment history for this commission
        payments = cls.objects.filter(agent_commission_id=commission_id)
        total_paid = payments.aggregate(
            total=models.Sum('payment_amount')
        )['total'] or 0
        # Outstanding = recognized - realized - deductible (if negative, return 0)
        commission_deductible = getattr(commission, 'commission_deductible', 0) or 0
        outstanding = max(0, commission.revenue_recognized - commission.revenue_realized - commission_deductible)
        return {
            'commission_id': commission_id,
            'revenue_recognized': commission.revenue_recognized,
            'revenue_realized': commission.revenue_realized,
            'commission_deductible': commission_deductible,
            'total_paid': total_paid,
            'outstanding': outstanding,
            'payment_count': payments.count()
        }

    @classmethod
    def get_incentive_outstanding_amount(cls, incentive_id):
        """Calculate outstanding amount for a specific incentive"""
        from .crmf_incentives import Incentive
        incentive = Incentive.objects.get(id=incentive_id)
        return incentive.incentive_amount

    @classmethod
    def get_incentive_payment_summary(cls, incentive_id):
        """Get detailed payment summary for an incentive"""
        from .crmf_incentives import Incentive
        incentive = Incentive.objects.get(id=incentive_id)
        
        # Get payment history for this incentive
        payments = cls.objects.filter(incentive_id=incentive_id)
        total_paid = payments.aggregate(
            total=models.Sum('payment_amount')
        )['total'] or 0
        
        return {
            'incentive_id': incentive_id,
            'incentive_amount': incentive.incentive_amount,
            'total_paid': total_paid,
            'outstanding': incentive.incentive_amount - total_paid,
            'payment_count': payments.count()
        }
   