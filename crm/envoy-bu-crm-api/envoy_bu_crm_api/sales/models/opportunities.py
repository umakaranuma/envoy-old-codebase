from django.db import models
from django.utils import timezone

from envoy_bu_crm_api.sales.models.core_models import Channel, Contact, Country, Currency, Customer, Entity, Product, ProductGroup, User, VendorProducts
from envoy_bu_crm_api.sales.models.opportunity_health import OpportunityHealth
from envoy_bu_crm_api.sales.models.opportunity_status import OpportunityStatus

class Opportunity(models.Model):
    CORPORATE = "Corporate"
    PERSONAL = "Personal"
    TYPE_CHOICES = [
        (CORPORATE, "Corporate"),
        (PERSONAL, "Personal"),
    ]
    
    TRANSACTION_TYPE_CHOICES = [
        ("new", "New"),
        ("renewal", "Renewal")
    ]
    
    entity = models.ForeignKey(Entity, on_delete=models.RESTRICT)
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    contact_number = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=255, blank=True, null=True) 
    contact = models.ForeignKey(
        Contact, on_delete=models.SET_NULL, null=True, blank=True, db_column="contact_id"
    )
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    code = models.CharField(max_length=255, unique=True)
    channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, blank=True, null=True)
    last_contacted_date = models.DateField(blank=True, null=True)
    campaign_id = models.BigIntegerField(blank=True, null=True)
    stage = models.ForeignKey(OpportunityStatus, on_delete=models.RESTRICT)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    current_health = models.ForeignKey(
        OpportunityHealth, on_delete=models.SET_NULL, blank=True, null=True, related_name="opportunities"
    )
    sales_agent = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,related_name="sales_agent_opportunities")
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_opportunities"
    )
    account_manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,related_name="account_manager_opportunities")
    currency = models.ForeignKey(Currency, on_delete=models.RESTRICT)
    sort_index = models.FloatField(blank=True, null=True)
    lead_value = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    sale_value = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES, blank=True, null=True)
    issued_policy_id = models.BigIntegerField(blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, help_text="Product when product_type is 'product'")
    product_group = models.ForeignKey(ProductGroup, on_delete=models.SET_NULL, null=True, blank=True, help_text="Product group when product_type is 'group'")
    # created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = "crm_opportunities"

    def __str__(self):
        return self.title