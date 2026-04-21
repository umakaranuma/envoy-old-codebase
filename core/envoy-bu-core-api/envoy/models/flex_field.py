from django.db import models

class FlexField(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    entity_type = models.CharField(max_length=255,blank=False,null=False)
    field_code = models.CharField(max_length=255, blank=False,null=False, default=None)
    field_label = models.CharField(max_length=255, blank=False,null=False, default=None)
    data_type = models.CharField(max_length=255, blank=False,null=False, default=None)
    default_value = models.CharField(max_length=255, blank=True, null=True)
    is_mandatory = models.BooleanField(default=False)
    is_enabled = models.BooleanField(default=False)
    is_fixed = models.BooleanField(default=False)

    class Meta:
        db_table = "core_flex_fields"

    def __str__(self):
        return f"{self.entity_type} - {self.field_label}"
