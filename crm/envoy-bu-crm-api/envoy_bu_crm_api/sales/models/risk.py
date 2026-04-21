from django.db import models
from django.utils import timezone

from envoy_bu_crm_api.sales.models.core_models import Customer,User
from envoy_bu_crm_api.sales.models.OpportunityType import OpportunityType


class Risk(models.Model):
    """
    Model representing individual risks in the system.
    Based on the image specifications with columns: id, code, customer_id, risk_type_id
    """
    id = models.AutoField(primary_key=True, help_text="Unique risk ID")
    code = models.CharField(max_length=50, help_text="Risk code like R001-car, R002-car")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='risks', null=True, blank=True)
    risk_type = models.ForeignKey(OpportunityType, on_delete=models.SET_NULL, null=True, blank=True, related_name='risks')
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
        
    # Soft delete fields
    is_deleted = models.BooleanField(default=False, help_text="Whether this record is soft deleted")
    deleted_at = models.DateTimeField(null=True, blank=True, help_text="When this record was soft deleted")
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, help_text="User who deleted this record")


    class Meta:
        db_table = 'crm_risks'
        verbose_name = 'Risk'
        verbose_name_plural = 'Risks'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['customer']),
        ]

    def __str__(self):
        return f"{self.code} - {self.risk_type.title if self.risk_type else 'No Type'}"