from django.db import models

from envoy.models.modules import Module

class Action(models.Model):
    id = models.AutoField(primary_key=True)
    entity = models.CharField(max_length=50,blank=False, null=False)
    action = models.CharField(max_length=50,blank=False, null=False)
    remarks = models.CharField(max_length=320, blank=True, null=True)
    can_be_permission = models.BooleanField(default=False)
    module = models.ForeignKey(Module,on_delete=models.RESTRICT, blank=False, null=False)

    class Meta:
        db_table = "core_actions"

    def __str__(self):
        return f"Action: {self.entity} - {self.action}"
