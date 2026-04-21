from django.db import models
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from envoy_bu_policy_api.policy.models.crmp_request_policies import RequestPolicy

class IssuedPolicy(models.Model):
    # Policy details 
    brokerage_policy_id = models.CharField(max_length=255)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2,blank=True, null=True)
    credit_period_days = models.IntegerField()
    credit_age_days = models.IntegerField()  # Auto-calculated, not editable by users
    insurer_invoice_id = models.CharField(max_length=255, blank=False, null=False)  # Insurer Invoice ID
    insurer_policy_id = models.CharField(max_length=255, blank=True, null=True,)  # Insurer Invoice ID
    sum_insured = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    premium_amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    policy_effective_date = models.DateField(blank=True, null=True)
    policy_document = models.URLField(blank=True, null=True) 
    policy_document_name = models.CharField(max_length=255, blank=True, null=True)
    policy_request = models.ForeignKey(RequestPolicy, related_name='policy_req', on_delete=models.CASCADE,blank=True,null=True)
    entity = models.ForeignKey("core_models.Entity", related_name='policy_entity', on_delete=models.CASCADE,default=1)
    remarks = models.TextField(blank=True, null=True)
    policy_base=models.ForeignKey("policy.PolicyBase", related_name='policy_issued_base', on_delete=models.CASCADE)
    invoice_document = models.URLField(blank=True, null=True) 
    invoice_document_name = models.CharField(max_length=255, blank=True, null=True)
    initial_premium_amount=models.DecimalField(max_digits=12, decimal_places=2,blank=True, null=True)
    is_renewal = models.BooleanField(default=False,null=True,blank=True)
    
    class Meta:
        db_table = "crmp_issued_policies"

    def __str__(self):
        return f"Policy {self.brokerage_policy_id}"
    
    def calculate_credit_age(self):
        """
        Calculate credit age based on:
        - Credit period starts from policy_effective_date (issue date)
        - Credit age = days after credit period ends without full payment
        - Returns 0 if fully paid or still within credit period
        """
        # If fully paid, credit age is 0
        if self.paid_amount and self.premium_amount:
            if Decimal(str(self.paid_amount)) >= Decimal(str(self.premium_amount)):
                return 0
        
        # Get the issue date (policy_effective_date)
        issue_date = self.policy_effective_date
        if not issue_date:
            # Fallback to start_date if policy_effective_date is not set
            issue_date = self.start_date.date() if isinstance(self.start_date, timezone.datetime) else self.start_date
        
        if not issue_date:
            return 0
        
        # Calculate credit period end date
        credit_period_end_date = issue_date + timedelta(days=self.credit_period_days)
        
        # Get current date
        today = timezone.now().date()
        
        # Credit age starts from the day after credit period ends
        if today > credit_period_end_date:
            credit_age = (today - credit_period_end_date).days
            return max(0, credit_age)
        
        return 0
    
    def update_credit_age(self):
        """Update credit_age_days field with calculated value"""
        self.credit_age_days = self.calculate_credit_age()
        self.save(update_fields=['credit_age_days'])

