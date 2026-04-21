from django.db import models


class EntityApprovalRule(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    entity_type = models.CharField(max_length=255, null=True, blank=True)
    action = models.CharField(max_length=255, null=True, blank=True)
    rule = models.JSONField(null=True, blank=True)
    default_status = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = "core_entity_approval_rules"

    def __str__(self):
        return self.entity_type
