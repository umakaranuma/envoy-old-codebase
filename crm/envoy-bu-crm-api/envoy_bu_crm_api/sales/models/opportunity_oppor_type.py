from django.db import models


class OpportunityOpporType(models.Model):
    opportunity = models.ForeignKey("sales.Opportunity", on_delete=models.CASCADE)
    opportunity_type = models.ForeignKey("sales.OpportunityType", on_delete=models.RESTRICT)

    class Meta:
        db_table = "crm_oppor_opportunity_types"