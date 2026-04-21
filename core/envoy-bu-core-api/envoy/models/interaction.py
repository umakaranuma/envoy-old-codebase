from django.db import models
from envoy.models import Contact, Channel ,Customer, Task, User
from envoy.models.entity import Entity
# from envoy_bu_crm_api.sales.models.opportunity_status import OpportunityStatus
# from envoy_bu_crm_api.sales.models.opportunity import Opportunity
# from  import Channel, Contact, Customer, Task, User


class Intraction(models.Model):
    """Model representing interactions in the CRM system"""

    id = models.AutoField(primary_key=True,unique=True,null=False,blank=False)
    channel = models.ForeignKey(Channel, on_delete=models.RESTRICT)
    contact = models.ForeignKey(Contact, on_delete=models.CASCADE, null=True, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    opportunity_id = models.IntegerField( null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, null=True, blank=True)
    notes = models.TextField(blank=True, null=True)
    contact_by = models.ForeignKey(User, on_delete=models.RESTRICT, null=False, blank= False)
    opportunity_status_id = models.IntegerField( null=True, blank=True)
    date = models.DateField(null=False)
    entity = models.ForeignKey(Entity ,on_delete=models.CASCADE , null=False, blank= False) 

    class Meta:
        db_table = "core_intractions"

    def __str__(self):
        return f"Intraction {self.id} - Channel: {self.channel}"
