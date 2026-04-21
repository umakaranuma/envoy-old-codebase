from django.db import models

from envoy.models.form_custom_form_setup import CoreFormCustomFormStep
from envoy.models.form_templetes import CoreTemplate


class CoreFormCustomFormPanel(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True)
    form = models.ForeignKey(CoreTemplate, on_delete=models.CASCADE, db_column='form_id')
    step = models.ForeignKey(CoreFormCustomFormStep, null=True, blank=True, on_delete=models.SET_NULL, db_column='step_id')
    order_number = models.FloatField(default=1.0) 

    class Meta:
        db_table = "core_form_custom_form_panels"