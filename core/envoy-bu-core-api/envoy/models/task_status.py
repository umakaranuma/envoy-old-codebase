from django.db import models


class TaskStatus(models.Model):
    class StatusType(models.TextChoices):
        TODO = "Todo", "To Do"
        IN_PROGRESS = "Inprogress", "In Progress"
        DONE = "Done", "Done"

    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=80, unique=True, blank=False, null=False)
    description = models.CharField(max_length=250, blank=True, null=True)
    type = models.CharField(max_length=20, choices=StatusType.choices, blank=False, null=False)
    color = models.CharField(max_length=100, default="#eeeeef", blank=False, null=False)
    sort_index = models.FloatField(blank=True, null=True)


    class Meta:
        db_table = "core_task_status"

    def __str__(self):
        return f"{self.name} - {self.type}"
