# from django.db import models

# from envoy_bu_policy_api.policy.models.crmp_policy_base import PolicyBase


# class PolicyBaseProduct(models.Model):
#     policy_base = models.ForeignKey(PolicyBase, on_delete=models.CASCADE, related_name="products")
#     product = models.ForeignKey("core_models.VendorProduct", on_delete=models.CASCADE, null=True, blank=True)
#     product_group = models.ForeignKey("core_models.ProductGroup", on_delete=models.CASCADE, null=True, blank=True)

#     class Meta:
#         db_table = "crmp_policy_base_products"
#         unique_together = ("policy_base", "product")
#         constraints = [
#             models.CheckConstraint(
#                 check=(
#                     models.Q(product__isnull=False, product_group__isnull=True) |
#                     models.Q(product__isnull=True, product_group__isnull=False)
#                 ),
#                 name='product_or_group_required'
#             )
#         ]

#     def __str__(self):
#         return f"Policy Base: {self.policy_base_id} - Product: {self.product_id}"
