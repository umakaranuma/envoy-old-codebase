from django.db import models

from envoy_bu_policy_api.finance.controllers.utils import commission

class crmf_flex_field_entity(models.Model):
    """
    Model for storing mapping update history
    """
    id = models.AutoField(primary_key=True)
    flex_filed_id = models.IntegerField()
    entity_id = models.IntegerField()
    commission_setup_id = models.IntegerField(null=True, blank=True)
    payment_id = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'crmf_flex_field_entities'

    def __str__(self):
        return str(self.id)