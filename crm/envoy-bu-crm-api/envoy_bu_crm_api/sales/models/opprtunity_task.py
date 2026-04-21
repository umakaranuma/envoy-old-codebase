from django.db import models

from envoy_bu_crm_api.sales.models.core_models import Task


class OpportunityTask(models.Model):
    id = models.AutoField(primary_key=True)
    task = models.ForeignKey(Task, on_delete=models.RESTRICT,related_name="opportunity_tasks")  
    opportunity = models.ForeignKey("sales.Opportunity", on_delete=models.CASCADE)
    task_config = models.ForeignKey("task.TaskConfig", on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        db_table = "crm_opportunity_tasks"