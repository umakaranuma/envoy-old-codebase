from django.db import models

from envoy.models.form_custom_form_setup import CoreFormCustomFormStep
from envoy.models.form_elements import CoreFormElement
from envoy.models.form_panels import CoreFormCustomFormPanel

class CoreFormCustomFormElement(models.Model):
    label = models.CharField(max_length=200, null=True, blank=True)
    step = models.ForeignKey(CoreFormCustomFormStep, null=True, blank=True, on_delete=models.SET_NULL, db_column='step_id')
    panel = models.ForeignKey(CoreFormCustomFormPanel, null=True, blank=True, on_delete=models.SET_NULL, db_column='panel_id')
    element = models.ForeignKey(CoreFormElement, on_delete=models.CASCADE, db_column='element_id')
    is_required = models.BooleanField(default=False)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, db_column='parent_id')
    order_number = models.FloatField(null=True, blank=True)
    column_size = models.IntegerField()
    category = models.CharField(max_length=200,null=True, blank=True)
    code = models.CharField(max_length=200,null=True, blank=True)

    class Meta:
        db_table = "core_form_custom_form_elements"