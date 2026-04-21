from django.db import models
from .crmf_commision_setup import CommissionSetup

class AgentCommission(models.Model):
    brokerage_commission = models.ForeignKey(
        "finance.BrokerageCommission",
        on_delete=models.CASCADE,
        related_name='agent_commissions'
    )
    agent = models.ForeignKey(
        "core_models.User",
        on_delete=models.CASCADE,
        related_name='agent_commissions'
    )
    agent_commission_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Agent Commission Percentage"
    )
    agent_commission_type = models.CharField(max_length=20, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed'), ('flat', 'Flat')], default='percentage', help_text='Type of agent commission: percentage or fixed')
    target_achievement_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Target Achievement Amount"
    )
    bonus_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0,
        help_text="Bonus Amount"
    )
    revised_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0,
        help_text="Revised Amount"
    )
    revised_amount_percent = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0,
        help_text="Revised Amount Percent"
    )
    revised_amount_type = models.CharField(max_length=20, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed'), ('flat', 'Flat')], default='percentage', help_text='Type of revised amount: percentage or fixed')
    paid_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0,
        help_text="Paid Amount"
    )
    revenue_recognized = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Total Commission Amount"
    )
    revenue_realized = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        default=0,
        help_text="Amount Paid to Agent"
    )

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("issued", "Issued"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("cancelled", "Cancelled"),
        ("pending", "Pending"),                    # No settlements to agent
        ("partially_paid", "Partially Paid"),      # Partial settlements to agent
        ("fully_paid", "Fully Paid"),              # Full settlement to agent
    ]
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")

    entity = models.ForeignKey(
        "core_models.Entity",
        related_name="agent_commissions",
        on_delete=models.CASCADE,
        default=1
    )
    commission_setup=models.ForeignKey(CommissionSetup,related_name="agent_commissions",on_delete=models.PROTECT)
    commission_deductible = models.DecimalField(max_digits=12, decimal_places=2,blank=True,null=True)


    class Meta:
        db_table = "crmf_agent_commission"
        verbose_name = "Agent Commission"
        verbose_name_plural = "Agent Commissions"

