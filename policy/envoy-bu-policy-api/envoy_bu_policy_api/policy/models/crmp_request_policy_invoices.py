from django.db import models
from django.utils import timezone
from .crmp_request_policies import RequestPolicy
from .crmp_issued_policies import IssuedPolicy
from .crmp_endorsement_request import EndorsementRequest
from .crmp_endorsements_details import Endorsement

class RequestPolicyInvoice(models.Model):
    INVOICE_TYPE_CHOICES = [
        ('request', 'Request Policy'),
        ('issued', 'Issued Policy'),
        ('endorsement', 'Endorsement'),
        ('endorsement_request', 'Endorsement Request'),
    ]
    
    invoice_number = models.CharField(max_length=255, unique=True)
    invoice_date = models.DateField(default=timezone.now)
    due_date = models.DateField(null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    outstanding_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    remarks = models.TextField(blank=True, null=True)
    currency = models.CharField(max_length=3, default="USD")
    status = models.ForeignKey("core_models.Status", on_delete=models.CASCADE, default=1, null=True, blank=True)
    
    # Foreign key relationships to handle different types
    request_policy = models.ForeignKey(RequestPolicy, null=True, blank=True, on_delete=models.SET_NULL)
    issued_policy = models.ForeignKey(IssuedPolicy, null=True, blank=True, on_delete=models.SET_NULL)
    endorsement = models.ForeignKey(Endorsement, null=True, blank=True, on_delete=models.SET_NULL)
    endorsement_request = models.ForeignKey(EndorsementRequest, null=True, blank=True, on_delete=models.SET_NULL)
    invoice_type = models.CharField(max_length=20, choices=INVOICE_TYPE_CHOICES)
    entity = models.ForeignKey("core_models.Entity", related_name='invoice_entity', on_delete=models.CASCADE,default=1)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Default to 0 if total_amount or paid_amount is None
        self.total_amount = self.total_amount or 0
        self.paid_amount = self.paid_amount or 0
        self.issued_policy = self.issued_policy or None
        # Calculate outstanding_amount
        self.outstanding_amount = self.total_amount - self.paid_amount
        # If invoice_number is not set, generate it
        if not self.invoice_number:
            self.generate_invoice_number()

        super(RequestPolicyInvoice, self).save(*args, **kwargs)

    def generate_invoice_number(self):
        """Generate an invoice number without using the primary key"""
        invoice_type = self.invoice_type[:3].upper()  # Get first 3 chars of invoice type
        print(f"Invoice Type: {invoice_type}",self.invoice_type)
        today = timezone.now().strftime('%Y%m%d')  # Get current date in YYYYMMDD format
        
        # Generate a unique sequence here; for simplicity, we'll use a random string or something else
        # You can also use `uuid.uuid4()` or a custom sequence generator here
        unique_sequence = timezone.now().strftime('%H%M%S')  # Using time-based unique sequence for simplicity
        self.invoice_number = f"{invoice_type}-{today}-{unique_sequence}"

    def __str__(self):
        return f"Invoice {self.invoice_number} ({self.invoice_type})"
    
    class Meta:
        db_table = "crmp_invoices"

