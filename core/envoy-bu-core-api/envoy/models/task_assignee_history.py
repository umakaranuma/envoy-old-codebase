from django.db import models

from envoy.models.task import Task
from envoy.models.user import User

class TaskAssigneeHistory(models.Model):
    id = models.AutoField(primary_key=True, unique=True,blank=False,null=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="assignee_histories",blank=False,null=False)
    from_assigned = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="assigned_from_history",blank=False,null=False)
    to_assigned = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="assigned_to_history",blank=False,null=False)
    remark = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    changed_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="assignee_changes",blank=False,null=False)

    class Meta:
        db_table = "core_task_assignee_histories"

    def __str__(self):
        return f"Task {self.task.task} reassigned from {self.from_assigned.username} to {self.to_assigned.username}"
