from django.db import models

class Reason(models.Model):
    reason = models.CharField(max_length=255, unique=True, db_index=True)  # Unique in DB
    type_id = models.IntegerField(null=True, blank=True)  # Required
    allows_custom_reason = models.BooleanField(default=False)  # Default to False
    description = models.TextField(null=True, blank=True)  # Optional field

    class Meta:
        db_table = "core_reasons"

    def __str__(self):
        return self.reason