from django.db import models

from envoy.models.flex_field import FlexField

class FlexFieldOption(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    flex_field = models.ForeignKey(FlexField, on_delete=models.CASCADE, related_name="options",blank=False,null=False)
    value = models.CharField(max_length=255,blank=False,null=False)

    class Meta:
        db_table = "core_flex_field_options"

    def __str__(self):
        return f"{self.flex_field.field_label} - {self.value}"
