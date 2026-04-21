from django.db import models

class OpportunityStatus(models.Model):
    LEAD = "opportunity_lead"
    PROSPECT = "opportunity_prospect"
    QUALIFIED = "opportunity_qualified"
    WON = "opportunity_won"
    LOSS = "opportunity_loss"

    STATUS_CHOICES = [
        (LEAD, "LEAD"),
        (PROSPECT, "PROSPECT"),
        (QUALIFIED, "QUALIFIED"),
        (WON, "WON"),
        (LOSS, "LOSS"),
    ]

    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    type = models.CharField(max_length=30, choices=STATUS_CHOICES)
    color = models.CharField(max_length=100, default="#eeeeef")
    sort_index = models.FloatField(blank=True, null=True)

    class Meta:
        db_table = "crm_opportunity_statuses"

    def __str__(self):
        return self.name