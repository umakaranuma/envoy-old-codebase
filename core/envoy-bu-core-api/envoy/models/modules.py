from django.db import models

class Module(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=25, unique=True)
    key = models.CharField(max_length=255, unique=True)
    description = models.CharField(max_length=320, blank=True, null=True)

    class Meta:
        db_table = "core_modules"

    def __str__(self):
        return f"{self.name} ({self.key})"
