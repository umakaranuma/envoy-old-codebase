from django.db import models

from envoy.models.form_templetes import CoreTemplate



class CoreFormCustomFormStep(models.Model):
    form = models.ForeignKey(CoreTemplate, on_delete=models.CASCADE, db_column='form_id')
    title = models.CharField(max_length=200)
    step_number = models.FloatField()
    description = models.CharField(max_length=250, null=True, blank=True)

    class Meta:
        db_table = "core_form_custom_form_steps"