# from django.db import models

# class ClaimFormConfig(models.Model):
#     title = models.CharField(max_length=255)
#     form = models.ForeignKey("sales.Form", on_delete=models.CASCADE)
#     type = models.ForeignKey("sales.OpportunityType",on_delete=models.CASCADE,blank=True, null=True)

#     class Meta:
#         db_table = "crmp_claim_form_config"

#     def __str__(self):
#         return self.title
