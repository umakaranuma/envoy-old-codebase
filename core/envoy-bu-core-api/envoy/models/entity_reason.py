from django.db import models

from envoy.models.entity import Entity
from envoy.models.reason import Reason

class EntityReason(models.Model):
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)  # Required, Cascade on delete
    reason_fk = models.ForeignKey(Reason, null=True, blank=True, on_delete=models.SET_NULL,db_column="reason_id")  # Required, Set Null on delete
    reason = models.TextField(null=False, blank=False, db_column="reason")  # Required
    custom_reason = models.TextField(null=True, blank=True)  # Optional field

    class Meta:
        db_table = "core_entity_reasons"

    def __str__(self):
        return f"{self.entity} - {self.reason_text}"