from django.db import models

from envoy.models.task import Task
from envoy.models.task_status import TaskStatus
from envoy.models.user import User

class TaskStatusHistory(models.Model):
    id = models.AutoField(primary_key=True, unique=True,blank=False,null=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="status_histories",blank=False,null=False)
    task_status = models.ForeignKey(TaskStatus, on_delete=models.RESTRICT, related_name="status_changes",blank=False,null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="status_changeby",blank=False,null=False)
    remark = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "core_task_status_histories"

    def __str__(self):
        return f"{self.task.task} - {self.task_status.name} (Changed by {self.changed_by.username})"
