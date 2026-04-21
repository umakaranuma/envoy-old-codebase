from django.db import models



class OpportunityStatus(models.Model):
    LEAD = "LEAD"
    PROSPECT = "PROSPECT"
    QUALIFIED = "QUALIFIED"
    WON = "WON"
    LOSS = "LOSS"

    STATUS_CHOICES = [
        (LEAD, "Lead"),
        (PROSPECT, "Prospect"),
        (QUALIFIED, "Qualified"),
        (WON, "Won"),
        (LOSS, "Loss"),
    ]

    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=20, choices=STATUS_CHOICES)
    color = models.CharField(max_length=100, default="#eeeeef")
    sort_index = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "crm_opportunity_statuses"
        managed = False


class OpportunityHealth(models.Model):
    opportunity = models.ForeignKey("core_models.Opportunity", on_delete=models.CASCADE)
    date = models.DateField()
    health = models.IntegerField()

    class Meta:
        db_table = "crm_opportunity_health"
        managed = False

class Opportunity(models.Model):
    CORPORATE = "Corporate"
    PERSONAL = "Personal"

    TYPE_CHOICES = [
        (CORPORATE, "Corporate"),
        (PERSONAL, "Personal"),
    ]

    entity = models.ForeignKey("core_models.Entity", on_delete=models.RESTRICT)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    contact_number = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    
    
    contact = models.ForeignKey(
        "core_models.Contact", on_delete=models.SET_NULL, null=True, blank=True, db_column="contact_id"
    )

    customer = models.ForeignKey("core_models.Customer", on_delete=models.SET_NULL, null=True, blank=True)
    code = models.CharField(max_length=255, unique=True)
    channel = models.ForeignKey("core_models.Channel", on_delete=models.SET_NULL, blank=True, null=True)
    last_contacted_date = models.DateField(blank=True, null=True)
    campaign_id = models.BigIntegerField(blank=True, null=True)


    stage = models.ForeignKey("core_models.OpportunityStatus", on_delete=models.RESTRICT)

    remarks = models.CharField(max_length=255, blank=True, null=True)
    
    
    current_health = models.ForeignKey(
        OpportunityHealth, on_delete=models.SET_NULL, blank=True, null=True, related_name="opportunities"
    )

    sales_agent = models.ForeignKey("core_models.User", on_delete=models.SET_NULL, null=True, blank=True,related_name="sales_agent_opportunities")
    created_by = models.ForeignKey(
        "core_models.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="created_opportunities"
    )
    account_manager = models.ForeignKey("core_models.User", on_delete=models.SET_NULL, null=True, blank=True,related_name="account_manager_opportunities")

    currency = models.ForeignKey("core_models.Currency", on_delete=models.RESTRICT)
    sort_index = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "crm_opportunities"
        managed = False



class QuotationServiceProvider(models.Model):
    id = models.AutoField(primary_key=True)
    quotation_id =  models.BigIntegerField(blank=True, null=True) 
    service_provider_id =  models.BigIntegerField(blank=True, null=True)
    is_received = models.BooleanField(default=False)
    is_shortlisted = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    version = models.IntegerField(default=0)
    opportunity_id = models.BigIntegerField(blank=True, null=True)
    status = models.BigIntegerField(blank=True, null=True)

    class Meta:
        db_table = "crmq_quotation_service_providers"
        managed = False


class QuotationFormSubmission(models.Model):
    id = models.AutoField(primary_key=True)
    vendor_quotation_id = models.BigIntegerField(blank=True, null=True)
    form_submission_id = models.BigIntegerField(blank=True, null=True)
    by_user_id = models.BigIntegerField(blank=True, null=True)
    class Meta:
        db_table = 'crmq_quotation_form_submissions'
        verbose_name = 'QuotationFormSubmission'
        verbose_name_plural = 'QuotationFormSubmissions'
        managed = False




class TaskType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250, unique=True)
    description = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        db_table = "crm_task_types"
        managed = False


class TaskConfig(models.Model):
    task = models.CharField(max_length=250)
    code = models.CharField(max_length=80, unique=True)
    task_type = models.ForeignKey("TaskType", on_delete=models.RESTRICT)
    opportunity_status = models.ForeignKey("OpportunityStatus", on_delete=models.RESTRICT)
    expected_days = models.IntegerField(default=1,blank=True, null=True)
    reminder_expected_days = models.IntegerField(blank=True, null=True)
    sort_index = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "crm_task_configs"
        managed = False



class OpportunityTask(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey("core_models.Task", on_delete=models.RESTRICT,related_name="opportunity_tasks")  
    opportunity = models.ForeignKey("core_models.Opportunity", on_delete=models.CASCADE)
    task_config = models.ForeignKey("core_models.TaskConfig", on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = "crm_opportunity_tasks"
        managed = False


class Risk(models.Model):
    """
    Model representing individual risks in the system.
    Based on the image specifications with columns: id, code, cus_id, risk_type_id
    """
    id = models.AutoField(primary_key=True, help_text="Unique risk ID")
    code = models.CharField(max_length=50, help_text="Risk code like RIST0001, RISK0002")
    customer = models.ForeignKey("core_models.Customer", on_delete=models.CASCADE, related_name='risks', null=True, blank=True)
    risk_type = models.ForeignKey("core_models.OpportunityType", on_delete=models.SET_NULL, null=True, blank=True, db_column='risk_type_id', related_name='risks')
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # Soft delete fields
    is_deleted = models.BooleanField(default=False, help_text="Whether this record is soft deleted")
    deleted_at = models.DateTimeField(null=True, blank=True, help_text="When this record was soft deleted")
    deleted_by = models.ForeignKey("core_models.User", on_delete=models.SET_NULL, null=True, blank=True, help_text="User who deleted this record")

    class Meta:
        db_table = 'crm_risks'
        managed = False
        verbose_name = 'Risk'
        verbose_name_plural = 'Risks'
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['customer_id']),
        ]

    def __str__(self):
        return f"{self.code} - {self.risk_type_id.title if self.risk_type_id else 'No Type'}"






class RiskSubmission(models.Model):
    """
    Model representing the relationship between submissions and risks.
    Based on the image specifications with columns: id, risk_id, submission_id, lead_id
    """
    id = models.AutoField(primary_key=True)
    risk_id = models.ForeignKey("Risk", on_delete=models.CASCADE, db_column='risk_id', related_name='submission_risks')
    submission_id = models.IntegerField(help_text="ID of the submission")
    lead_id = models.ForeignKey("core_models.Opportunity", on_delete=models.SET_NULL, null=True, blank=True, db_column='lead_id', related_name='submission_risks')
    
    # Version field - tracks which version of the risk this submission uses
    version = models.IntegerField(default=1, help_text="Version number of the risk for this submission")
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'crm_risk_submissions'
        managed = False
        verbose_name = 'Submission Risk'
        verbose_name_plural = 'Submission Risks'
        unique_together = ['risk_id', 'submission_id']  # Prevent duplicate risk-submission combinations
        indexes = [
            models.Index(fields=['risk_id', 'version']),
            models.Index(fields=['submission_id']),
        ]