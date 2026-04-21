from django.db import models

from envoy.models.form_elements import CoreFormElement

class CoreFormGroupElementOption(models.Model):
    element = models.ForeignKey(CoreFormElement, on_delete=models.CASCADE, db_column='element_id')
    option_value = models.CharField(max_length=200)

    class Meta:
        db_table = "core_form_group_element_options"