from multiprocessing import Value
from django.db import models

from core_models.core_models import *



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

    entity = models.ForeignKey(Entity, on_delete=models.RESTRICT)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    contact_number = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True)
    
    
    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, blank=True, db_column="contact_id"
    )
    
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    code = models.CharField(max_length=255, unique=True)
    channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, blank=True, null=True)
    last_contacted_date = models.DateField(blank=True, null=True)
    campaign_id = models.BigIntegerField(blank=True, null=True)
    
    
    stage = models.ForeignKey(OpportunityStatus, on_delete=models.RESTRICT)

    remarks = models.CharField(max_length=255, blank=True, null=True)
    
    
    current_health = models.ForeignKey(
        OpportunityHealth, on_delete=models.SET_NULL, blank=True, null=True, related_name="opportunities"
    )

    sales_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,related_name="sales_agent_opportunities")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_opportunities"
    )
    account_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,related_name="account_manager_opportunities")
    
    currency = models.ForeignKey(Currency, on_delete=models.RESTRICT)
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
    task_type = models.ForeignKey(TaskType, on_delete=models.RESTRICT)
    opportunity_status = models.ForeignKey(OpportunityStatus, on_delete=models.RESTRICT)
    expected_days = models.IntegerField(default=1,blank=True, null=True)
    reminder_expected_days = models.IntegerField(blank=True, null=True)
    sort_index = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "crm_task_configs"
        managed = False



class OpportunityTask(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.RESTRICT,related_name="opportunity_tasks")  
    opportunity = models.ForeignKey("core_models.Opportunity", on_delete=models.CASCADE)
    task_config = models.ForeignKey(TaskConfig, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = "crm_opportunity_tasks"
        managed = False



class RiskDetail(models.Model):
    code = models.CharField(max_length=20, unique=True, editable=False)
    lead = models.ForeignKey(Opportunity, on_delete=models.CASCADE, )
    risk_type = models.ForeignKey(OpportunityType, on_delete=models.SET_NULL, null=True,blank=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    submission = models.ForeignKey(CoreFormSubmission, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    recommendation_document = models.FileField( null=True, blank=True)

    class Meta:
        db_table = 'crm_risk_details'
        managed = False

    def __str__(self):
        return self.code
