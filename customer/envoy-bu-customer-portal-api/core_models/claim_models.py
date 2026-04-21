from django.db import models

from core_models.crm_models import RiskSubmission

class Claim(models.Model):
    code = models.CharField(max_length=50, unique=True, blank=True)
    policy = models.ForeignKey("core_models.IssuedPolicy", on_delete=models.RESTRICT)
    customer = models.ForeignKey("core_models.Customer", on_delete=models.RESTRICT)
    status = models.ForeignKey("core_models.Status", on_delete=models.RESTRICT, limit_choices_to={'module': 'Claim'})
    risk_type = models.ForeignKey("core_models.OpportunityType", on_delete=models.RESTRICT, null=True, blank=True)
    insurer = models.ForeignKey("core_models.ServiceProvider", on_delete=models.RESTRICT, null=True, blank=True)
    template = models.ForeignKey("core_models.CoreTemplate", on_delete=models.RESTRICT, null=True, blank=True,related_name="claim_templates")
    evaluation_form = models.ForeignKey("core_models.CoreTemplate", on_delete=models.RESTRICT, null=True, blank=True,related_name="claim_evaluation_forms")
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_myself = models.BooleanField(default=True)
    reporter_name = models.CharField(max_length=255, null=True, blank=True)
    reporter_contact = models.CharField(max_length=100, null=True, blank=True)
    reporter_relationship = models.CharField(max_length=100, null=True, blank=True)
    indimation_time = models.DateTimeField(null=True, blank=True)


    class Meta:
        db_table = "crmp_claims"
        managed = False

    def __str__(self):
        return f"Claim #{self.code}"

    def save(self, *args, **kwargs):
        if not self.code:
            last_id = Claim.objects.all().order_by('id').last()
            next_id = last_id.id + 1 if last_id else 1
            self.code = f"CLM-{next_id:05d}"  # Format: CLM-00001
        super().save(*args, **kwargs)


#--------------------------------------------------------


class ClaimFormConfig(models.Model):
    title = models.CharField(max_length=255)
    form = models.ForeignKey("core_models.Form", on_delete=models.CASCADE)
    type = models.ForeignKey("core_models.OpportunityType",on_delete=models.CASCADE,blank=True, null=True)

    class Meta:
        db_table = "crmp_claim_form_config"
        managed = False

    def __str__(self):
        return self.title


#--------------------------------------------------------

class ClaimFormSubmission(models.Model):
    EVALUATION = 'evaluation'
    INCIDENT_INFO = 'incident_info'
    SUBMISSION_TYPE_CHOICES = [
        (EVALUATION, 'Evaluation'),
        (INCIDENT_INFO, 'Incident Info'),
    ]

    claim = models.ForeignKey(Claim, on_delete=models.CASCADE)
    form_submission = models.ForeignKey("core_models.CoreFormSubmission", on_delete=models.CASCADE)
    submission_type = models.CharField(
        max_length=20,
        choices=SUBMISSION_TYPE_CHOICES,
        # default=INCIDENT_INFO,
        null=True,
        help_text="Defines the type of claim form submission"
    )

    class Meta:
        db_table = "crmp_claim_form_submission"
        managed = False

    def __str__(self):
        return f"{self.get_submission_type_display()} - Submission {self.form_submission_id}"


#--------------------------------------------------------

class ClaimRisk(models.Model):
    """
    Model to store the relationship between claims and risk submissions.
    This allows a claim to be associated with multiple risk submissions.
    """
    claim = models.ForeignKey(
        Claim,
        related_name='claim_risks',
        on_delete=models.CASCADE,
        help_text="The claim this risk submission is associated with"
    )
    risk_submission = models.ForeignKey(
        RiskSubmission,
        related_name='claim_risks',
        on_delete=models.CASCADE,
        help_text="The risk submission associated with this claim"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "crmp_claim_risks"
        managed = False
        