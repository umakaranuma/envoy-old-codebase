from django.db import models

class CoverageType(models.Model):
    name = models.CharField(max_length=255)  
    description = models.TextField(blank=True, null=True)  

    def __str__(self):
        return self.name

    class Meta:
        db_table = "crmp_coverage_types"