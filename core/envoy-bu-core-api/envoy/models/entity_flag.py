from django.db import models

from envoy.models.entity import Entity
from envoy.models.flag import Flag
from envoy.models.reason import Reason

class EntityFlag(models.Model):
    entity = models.ForeignKey(Entity,on_delete=models.CASCADE,related_name="flags",null=False, blank=False)
    flag = models.ForeignKey(Flag,on_delete=models.RESTRICT,related_name="entity_flags",null=False, blank=False)
    reason = models.ForeignKey(Reason,on_delete=models.SET_NULL,related_name="entity_reasons",null=True, blank=True)

    class Meta:
        db_table = "core_entity_flags"
        unique_together = ("entity", "flag")

    def __str__(self):
        return f"{self.entity} - {self.flag}"
