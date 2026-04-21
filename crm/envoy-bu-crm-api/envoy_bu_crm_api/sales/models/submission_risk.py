from django.db import models
from django.utils import timezone

from envoy_bu_crm_api.sales.models.risk import Risk
from envoy_bu_crm_api.sales.models.opportunities import Opportunity


class RiskSubmission(models.Model):
    """
    Model representing the relationship between submissions and risks.
    Based on the image specifications with columns: id, risk_id, submission_id, lead_id
    """
    id = models.AutoField(primary_key=True)
    risk = models.ForeignKey(Risk, on_delete=models.CASCADE, related_name='submission_risks')
    submission_id = models.IntegerField(help_text="ID of the submission")
    lead = models.ForeignKey(Opportunity, on_delete=models.SET_NULL, null=True, blank=True, related_name='submission_risks')
    
    # Version field - tracks which version of the risk this submission uses
    version = models.IntegerField(default=1, help_text="Version number of the risk for this submission")
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_risk_submissions'
        verbose_name = 'Submission Risk'
        verbose_name_plural = 'Submission Risks'
        unique_together = ['risk_id', 'submission_id']  # Prevent duplicate risk-submission combinations
        indexes = [
            models.Index(fields=['risk_id', 'version']),
            models.Index(fields=['submission_id']),
        ]

    @classmethod
    def get_latest_version_submissions(cls, risk_id):
        """
        Get all submissions for the latest version of a risk
        """
        # Get the latest version number for this risk
        latest_version = cls.objects.filter(risk_id=risk_id).aggregate(
            max_version=models.Max('version')
        )['max_version'] or 0
        
        # Return submissions for the latest version
        return cls.objects.filter(risk_id=risk_id, version=latest_version)

    @classmethod
    def create_new_version_submission(cls, risk_id, submission_id, lead_id):
        """
        Create a new submission for a risk with incremented version
        """
        # Get the latest version number for this risk
        latest_version = cls.objects.filter(risk_id=risk_id).aggregate(
            max_version=models.Max('version')
        )['max_version'] or 0
        
        # Create new submission with incremented version
        return cls.objects.create(
            risk_id_id=risk_id,
            submission_id=submission_id,
            lead_id=lead_id,
            version=latest_version + 1
        )

    def __str__(self):
        return f"Submission {self.submission_id} - Risk {self.risk_id.code} v{self.version}"
