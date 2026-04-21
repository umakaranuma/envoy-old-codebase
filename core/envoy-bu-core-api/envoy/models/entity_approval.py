from django.db import models

from envoy.models.entity import Entity

class EntityApproval(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    entity_id = models.BigIntegerField(null=True, blank=True)
    user = models.BigIntegerField(null=True, blank=True)
    role = models.BigIntegerField(null=True, blank=True)
    level = models.IntegerField(null=True, blank=True)
    status = models.CharField(max_length=100, default="open")
    remarks = models.TextField(null=True, blank=True)
    approved_by = models.BigIntegerField(null=True, blank=True)
    date = models.DateTimeField( null=True, blank=True)
    deleted_at = models.DateField(null=True , blank=True)

    class Meta:
        db_table = "core_entity_approvals"

    def __str__(self):
        return self.entity_id
