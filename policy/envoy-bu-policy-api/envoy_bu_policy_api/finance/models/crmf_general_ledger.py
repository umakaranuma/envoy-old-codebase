from django.db import models
from core_models.core_models import Entity
from core_models.crm_models import ServiceProvider

class GeneralLedger(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ("cash", "Cash"),
        ("bank_transfer", "Bank Transfer"),
        ("cheque", "Cheque"),
        ("credit_card", "Credit Card"),
        ("other", "Other"),
    ]

    LEDGER_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("completed", "Completed"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    ]

    invoice_number = models.CharField(max_length=50)
    transaction_date = models.DateField()
    payment_amount = models.DecimalField(max_digits=15, decimal_places=2)
    payer = models.ForeignKey(ServiceProvider, related_name='general_ledger_entries', on_delete=models.CASCADE)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    payment_id = models.CharField(max_length=100, unique=True)
    ledger_status = models.CharField(max_length=20, choices=LEDGER_STATUS_CHOICES, default="pending")
    remarks = models.TextField(blank=True, null=True)
    entity = models.ForeignKey(Entity, related_name='general_ledger_entries', on_delete=models.CASCADE, default=1)

    class Meta:
        db_table = "crmf_general_ledger"
        verbose_name = "General Ledger Entry"
        verbose_name_plural = "General Ledger Entries"
        ordering = ['-transaction_date', 'invoice_number']

    def __str__(self):
        return f"{self.invoice_number} - {self.transaction_date}"

    def save(self, *args, **kwargs):
        if not self.payment_id:
            # Generate payment ID
            last_entry = GeneralLedger.objects.order_by('-payment_id').first()
            
            if last_entry:
                last_num = int(last_entry.payment_id.replace("PAY", ""))
                new_num = last_num + 1
            else:
                new_num = 1
                
            self.payment_id = f"PAY{new_num:06d}"
            
        super().save(*args, **kwargs) 