from django.db import models

from envoy.models.user import User

class Entity(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="entities_created",null=True, blank=True, default=None
    )
    approvel_status = models.BooleanField(default=False,)
    updated_by = models.ForeignKey(User, on_delete=models.RESTRICT, related_name="entities_updated",null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_entities"

    def __str__(self):
        return f"Entity {self.id} - {self.type}"
