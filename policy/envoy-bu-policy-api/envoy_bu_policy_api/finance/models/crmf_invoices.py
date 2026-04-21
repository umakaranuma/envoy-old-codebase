from django.db import models
from core_models.core_models import ServiceProvider
from envoy_bu_policy_api.policy.models.crmp_issued_policies import IssuedPolicy
from envoy_bu_policy_api.policy.models.crmp_endorsements_details import Endorsement
from .crmf_invoice_types import InvoiceType

class Invoice(models.Model):
    INVOICE_TYPE_CHOICES = [
        ("credit_note", "Credit Note"),
        ("debit_note", "Debit Note"),
    ]
    invoice_number = models.CharField(max_length=255, unique=True)
    invoice_date = models.DateField(blank=True, null=True)
    credit_age_days = models.IntegerField(default=0)
    credit_period_days = models.IntegerField(default=0)
    due_date = models.DateField(null=True, blank=True)
    invoice_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    outstanding_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remarks = models.TextField(blank=True, null=True)
    issued_policy = models.ForeignKey(
        IssuedPolicy, null=True, blank=True, on_delete=models.SET_NULL
    )
    endorsement = models.ForeignKey(
        Endorsement, null=True, blank=True, on_delete=models.SET_NULL
    )
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES, blank=True, null=True)
    entity = models.ForeignKey(
        "core_models.Entity",
        related_name="invoices_entity",
        on_delete=models.CASCADE,
        default=1,
    )
    insurer = models.ForeignKey(
        ServiceProvider,
        related_name="invoices_insurer",
        on_delete=models.CASCADE,
        default=1,
    )
    insured = models.ForeignKey(
        "core_models.Customer",
        related_name="invoices_insured",
        on_delete=models.CASCADE,
        default=1,
    )
    last_paid_date = models.DateField(null=True, blank=True)
    transaction_type = models.ForeignKey(InvoiceType, on_delete=models.PROTECT, related_name='invoices',null=True, blank=True)
    product = models.ForeignKey("core_models.Product", related_name="finance_product", on_delete=models.CASCADE)
    status = models.ForeignKey("core_models.Status", on_delete=models.CASCADE, null=True, blank=True) #status of the invoice (paid, pending, partially paid, etc.)
    class Meta:
        db_table = "crmf_invoices"
