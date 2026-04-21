from django.db import models
from envoy.models import ProductGroup, Team  

class ProductGroupTeam(models.Model):
    id = models.AutoField(primary_key=True)
    product_group = models.ForeignKey(ProductGroup, on_delete=models.CASCADE, related_name="product_group_teams")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_product_groups")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_product_group_teams"
        # unique_together = ("product_group", "team") 

    def __str__(self):
        return f"{self.product_group.name} - {self.team.name}"
