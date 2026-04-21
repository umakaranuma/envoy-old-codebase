from django.db import models

from envoy_bu_crm_api.sales.models.opportunity_status import OpportunityStatus
from envoy_bu_crm_api.task.models.task_type import TaskType
from django.db.models import Value

class TaskConfig(models.Model):
    task = models.CharField(max_length=250)
    code = models.CharField(max_length=80, unique=True)
    task_type = models.ForeignKey("task.TaskType", on_delete=models.RESTRICT)
    opportunity_status = models.ForeignKey("sales.OpportunityStatus", on_delete=models.RESTRICT)
    expected_days = models.IntegerField(default=1, blank=True, null=True)
    reminder_expected_days = models.IntegerField(blank=True, null=True)
    sort_index = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "crm_task_configs"

    def __str__(self):
        return self.code