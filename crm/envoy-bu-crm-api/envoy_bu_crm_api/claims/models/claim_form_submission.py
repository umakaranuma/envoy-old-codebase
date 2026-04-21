# from django.db import models
# from envoy_bu_crm_api.claims.models.claim import Claim
# # from envoy_bu_crm_api.claims.models.claim_form_config import ClaimFormConfig

# class ClaimFormSubmission(models.Model):
#     EVALUATION = 'evaluation'
#     INCIDENT_INFO = 'incident_info'
#     SUBMISSION_TYPE_CHOICES = [
#         (EVALUATION, 'Evaluation'),
#         (INCIDENT_INFO, 'Incident Info'),
#     ]

#     claim = models.ForeignKey(Claim, on_delete=models.CASCADE)
#     form_submission = models.ForeignKey("sales.CoreFormSubmission", on_delete=models.CASCADE)
#     submission_type = models.CharField(
#         max_length=20,
#         choices=SUBMISSION_TYPE_CHOICES,
#         # default=INCIDENT_INFO,
#         null=True,
#         help_text="Defines the type of claim form submission"
#     )

#     class Meta:
#         db_table = "crmp_claim_form_submission"

#     def __str__(self):
#         return f"{self.get_submission_type_display()} - Submission {self.form_submission_id}"
