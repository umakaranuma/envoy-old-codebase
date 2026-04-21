from django.db import models

class OpportunityType(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "crm_opportunity_types"

    def __str__(self):
        return self.title
