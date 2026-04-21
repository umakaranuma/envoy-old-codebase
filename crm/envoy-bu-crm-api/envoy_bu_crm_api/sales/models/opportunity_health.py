from django.db import models


class OpportunityHealth(models.Model):
    opportunity = models.ForeignKey("sales.Opportunity", on_delete=models.CASCADE)
    date = models.DateField()
    health = models.IntegerField()

    class Meta:
        db_table = "crm_opportunity_health"
