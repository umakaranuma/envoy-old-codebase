from django.db import models
from envoy.models.user import User

from envoy.models.task_status import TaskStatus



class Task(models.Model):
    id = models.AutoField(primary_key=True, unique=True,null=False,blank=False)
    code = models.CharField(max_length=20, blank=False, null=False)
    task = models.CharField(max_length=250, blank=False, null=False)
    description = models.TextField(blank=True, null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_tasks")
    assigned_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    task_status = models.ForeignKey(TaskStatus, on_delete=models.RESTRICT, related_name="tasks")
    sort_index = models.FloatField(blank=True, null=True)


    class Meta:
        db_table = "core_tasks"

    def __str__(self):
        return f"{self.task} - {self.task_status.name}"
