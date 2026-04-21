from django.db import models
from envoy.models import Product, Team  # Adjust import paths as needed

class ProductTeam(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_teams")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="team_products")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "core_product_teams"
        unique_together = ("product", "team")  # Ensures unique pairing

    def __str__(self):
        return f"{self.product.name} - {self.team.name}"
