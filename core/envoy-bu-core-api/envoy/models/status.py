from django.db import models


class Status(models.Model):

    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=80, blank=False, null=False)
    description = models.CharField(max_length=250, blank=True, null=True)
    type = models.CharField(max_length=20, blank=False, null=True)
    module = models.CharField(max_length=200, blank=True, null=True)
    color = models.CharField(max_length=100, default="#eeeeef", blank=False, null=False)
    sort_index = models.FloatField(blank=True, null=True)


    class Meta:
        db_table = "core_status"
        verbose_name = 'Status'
        unique_together = ('module', 'name')

    def __str__(self):
        return self.id
