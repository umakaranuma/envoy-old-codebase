from django.db import models

class FlexValue(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    entity = models.ForeignKey("Entity", on_delete=models.CASCADE, related_name="flex_values")
    flex_values = models.JSONField(default=dict)

    class Meta:
        db_table = "core_flex_values"

    def __str__(self):
        return f"Flex Values for Entity {self.entity.id}"