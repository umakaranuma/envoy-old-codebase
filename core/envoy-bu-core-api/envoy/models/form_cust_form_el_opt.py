from django.db import models

from envoy.models.form_custom_elements import CoreFormCustomFormElement


class CoreFormCustomFormElementOption(models.Model):
    element = models.ForeignKey(CoreFormCustomFormElement, on_delete=models.CASCADE, db_column='element_id',related_name='options')
    option_value = models.CharField(max_length=200)

    class Meta:
        db_table = "core_form_custom_form_element_options"