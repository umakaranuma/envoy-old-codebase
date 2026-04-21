from django.db import models

from envoy.models.form_custom_elements import CoreFormCustomFormElement

class CoreFormDisplayElementValue(models.Model):
    element = models.ForeignKey(CoreFormCustomFormElement, on_delete=models.CASCADE, db_column='element_id')
    value = models.TextField()

    class Meta:
        db_table = "core_form_display_element_values"
