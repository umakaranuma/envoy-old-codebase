from django.db import models
from core_models.core_models import Entity

class ChartOfAccount(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ("asset", "Asset"),
        ("liability", "Liability"),
        ("equity", "Equity"),
        ("revenue", "Revenue"),
        ("expense", "Expense"),
    ]

    account_number = models.CharField(max_length=50, unique=True)
    account_name = models.CharField(max_length=255)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
  

    class Meta:
        db_table = "crmf_chart_of_account"
        verbose_name = "Chart of Account"
        verbose_name_plural = "Chart of Accounts"
        ordering = ['account_number']

    def __str__(self):
        return f"{self.account_number} - {self.account_name}"

