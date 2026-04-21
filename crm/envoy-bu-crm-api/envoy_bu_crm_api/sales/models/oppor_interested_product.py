from django.db import models

from envoy_bu_crm_api.sales.models.core_models import Product
from envoy_bu_crm_api.sales.models.opportunities import Opportunity

class OpportunityInterestedProduct(models.Model):
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)

    class Meta:
        db_table = "crm_oppor_interested_products"