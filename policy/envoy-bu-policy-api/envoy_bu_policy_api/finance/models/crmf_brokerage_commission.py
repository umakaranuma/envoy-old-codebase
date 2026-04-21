from django.db import models
from .crmf_invoices import Invoice
from .crmf_commision_setup import CommissionSetup
class BrokerageCommission(models.Model):
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE, related_name="brokerage_commission")
    brokerage_revenue_percent = models.DecimalField(max_digits=20, decimal_places=3)
    brokerage_revenue_type = models.CharField(max_length=20, choices=[('percentage', 'Percentage'), ('fixed', 'Fixed'), ('flat', 'Flat')], default='percentage', help_text='Type of brokerage revenue: percentage or fixed')
    revenue_recognized = models.DecimalField(max_digits=20, decimal_places=2)
    commission_deductible = models.DecimalField(max_digits=20, decimal_places=2)
    revenue_realized = models.DecimalField(max_digits=20, decimal_places=2)
    overriding_commission_amount = models.DecimalField(max_digits=20, decimal_places=2)
    agent_commission = models.DecimalField(max_digits=20, decimal_places=2, default=0, help_text="Commission amount for the agent")
    commission_setup=models.ForeignKey(CommissionSetup,related_name="brokerage_commission",on_delete=models.PROTECT)
    entity = models.ForeignKey(
        "core_models.Entity",
        related_name="brokerage_commissions",
        on_delete=models.CASCADE,
        default=1
    )

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("issued", "Issued"),
        ("paid", "Paid"),
        ("overdue", "Overdue"),
        ("cancelled", "Cancelled"),
        ("pending", "Pending"),                    # No commission received yet (no customer settlements)
        ("partially_received", "Partially Received"), # Customer partial payment, insurer partial payment
        ("received_in_full", "Received in Full"),   # Customer complete payment, commission received in full
    ]
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="pending")

    class Meta:
        db_table = "crmf_brokerage_commission"
        verbose_name = "Brokerage Commission"
        verbose_name_plural = "Brokerage Commissions"

    def __str__(self):
        return f"Commission for Invoice {self.invoice.invoice_number}"

