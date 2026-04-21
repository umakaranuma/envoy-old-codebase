from django.db import models

from envoy.models.form_custom_elements import CoreFormCustomFormElement
from envoy.models.form_elements import CoreFormElement
from envoy.models.form_submissions import CoreFormSubmission

class CoreFormSubmissionValue(models.Model):
    form_submission = models.ForeignKey(CoreFormSubmission, on_delete=models.CASCADE, db_column='form_submission_id')
    custom_form_element = models.ForeignKey(CoreFormCustomFormElement, on_delete=models.CASCADE, db_column='custom_form_element_id')
    form_element = models.ForeignKey(CoreFormElement, on_delete=models.CASCADE, db_column='form_element_id')
    value = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "core_form_submission_valuess"