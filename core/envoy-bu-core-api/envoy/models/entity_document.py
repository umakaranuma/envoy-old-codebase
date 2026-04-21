from django.db import models

from envoy.models.entity import Entity

class EntityDocument(models.Model):
    id = models.AutoField(primary_key=True, unique=True, blank=False)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE, related_name="documents",blank=False,null=False)
    doc = models.TextField(blank=True, null=True)
    name = models.CharField(max_length=255, blank=False)  
    type = models.CharField(max_length=255, blank=False)

    class Meta:
        db_table = "core_entity_docs"

    def __str__(self):
        return f"Document for Entity {self.entity.id}"