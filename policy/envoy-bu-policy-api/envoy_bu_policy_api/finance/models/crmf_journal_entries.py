from django.db import models
from core_models.core_models import Entity
from .crmf_chart_of_accounts import ChartOfAccount
from .crmf_invoices import Invoice

class JournalEntry(models.Model):
    entry_number = models.CharField(max_length=50)
    date = models.DateField()
    account = models.ForeignKey(ChartOfAccount, related_name='journal_entries', on_delete=models.CASCADE)
    debit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    credit_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    entity = models.ForeignKey(Entity, related_name='journal_entries', on_delete=models.CASCADE, default=1)
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="journal_entries", default=1)

    class Meta:
        db_table = "crmf_journal_entries"
        verbose_name = "Journal Entry"
        verbose_name_plural = "Journal Entries"
        ordering = ['-date', 'entry_number']

    def __str__(self):
        return f"{self.entry_number} - {self.date}"

    def save(self, *args, **kwargs):
        if not self.entry_number:
            # Generate entry number
            last_entry = JournalEntry.objects.order_by('-entry_number').first()
            
            if last_entry:
                last_num = int(last_entry.entry_number.replace("JE", ""))
                new_num = last_num + 1
            else:
                new_num = 1
                
            self.entry_number = f"JE{new_num:06d}"
            
        super().save(*args, **kwargs) 