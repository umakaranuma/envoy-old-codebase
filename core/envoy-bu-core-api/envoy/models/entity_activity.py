from django.db import models

from envoy.models.entity import Entity
from envoy.models.user import User
class EntityActivity(models.Model):
    entity = models.ForeignKey(Entity,on_delete=models.CASCADE,related_name="activities",null=False, blank=False)
    activity = models.TextField(null=False, blank=False)
    added_by = models.ForeignKey(User, on_delete=models.SET_NULL,null=True, blank=True, default=None
    )
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_entity_activities"

    def __str__(self):
        return f"{self.entity} - Activity"
