# from django.db import models

# class Claim(models.Model):
#     code = models.CharField(max_length=50, unique=True, blank=True)
#     policy = models.ForeignKey("policy.IssuedPolicy", on_delete=models.RESTRICT)
#     customer = models.ForeignKey("sales.Customer", on_delete=models.RESTRICT)
#     status = models.ForeignKey("sales.Status", on_delete=models.RESTRICT, limit_choices_to={'module': 'Claim'})
#     risk_type = models.ForeignKey("sales.OpportunityType", on_delete=models.RESTRICT, null=True, blank=True)
#     insurer = models.ForeignKey("sales.ServiceProvider", on_delete=models.RESTRICT, null=True, blank=True)
#     template = models.ForeignKey("sales.CoreTemplate", on_delete=models.RESTRICT, null=True, blank=True,related_name="claim_templates")
#     evaluation_form = models.ForeignKey("sales.CoreTemplate", on_delete=models.RESTRICT, null=True, blank=True,related_name="claim_evaluation_forms")
#     remarks = models.TextField(blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#     is_myself = models.BooleanField(default=True)
#     reporter_name = models.CharField(max_length=255, null=True, blank=True)
#     reporter_contact = models.CharField(max_length=100, null=True, blank=True)
#     reporter_relationship = models.CharField(max_length=100, null=True, blank=True)
#     indimation_time = models.DateTimeField(null=True, blank=True)



#     class Meta:
#         db_table = "crmp_claims"

#     def __str__(self):
#         return f"Claim #{self.code}"

#     def save(self, *args, **kwargs):
#         if not self.code:
#             last_id = Claim.objects.all().order_by('id').last()
#             next_id = last_id.id + 1 if last_id else 1
#             self.code = f"CLM-{next_id:05d}"  # Format: CLM-00001
#         super().save(*args, **kwargs)
