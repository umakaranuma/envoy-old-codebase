from django.db import models

from envoy.models.entity import Entity
from envoy.models.user import User

class EntityNote(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="notes",null=False,blank=False)
    is_high_priority = models.BooleanField(default=False)
    notes = models.TextField(blank=True, null=True)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True, default=None
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_entity_notes"

    def __str__(self):
        return f"Note for Entity {self.entity.id}"
