from django.db import models


class TaskType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=250, unique=True)
    description = models.CharField(max_length=250, blank=True, null=True)

    class Meta:
        db_table = "crm_task_types"

    def __str__(self):
        return self.name