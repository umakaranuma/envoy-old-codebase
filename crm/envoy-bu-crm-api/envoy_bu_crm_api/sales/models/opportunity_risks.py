# from django.db import models

# class OpportunityRisk(models.Model):
#     REQUEST_TYPE_CHOICES = [
#         ("new_business", "New Business"),
#         ("renewal", "Renewal")
#     ]

#     code = models.CharField(max_length=100, unique=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     entity = models.ForeignKey("sales.Entity", on_delete=models.CASCADE, null=True, blank=True)

#     customer = models.ForeignKey("sales.Customer", on_delete=models.CASCADE)
#     opportunity = models.ForeignKey("sales.Opportunity", on_delete=models.CASCADE,null=True, blank=True) 
#     risk_type = models.ForeignKey("sales.OpportunityType", on_delete=models.RESTRICT)

#     request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES)

#     class Meta:
#         db_table = "crm_opportunity_risks"
